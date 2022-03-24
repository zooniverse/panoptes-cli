import csv
import copy
import os
import re
import sys
import time
import yaml

import click
import humanize

from pathvalidate import is_valid_filename, sanitize_filename

from panoptes_cli.scripts.panoptes import cli
from panoptes_client import SubjectSet
from panoptes_client.panoptes import PanoptesAPIException

LINK_BATCH_SIZE = 10
MAX_PENDING_SUBJECTS = 50
MAX_UPLOAD_FILE_SIZE = 1024 * 1024
CURRENT_STATE_VERSION = 1

@cli.group(name='subject-set')
def subject_set():
    """Contains commands for managing subject sets."""
    pass


@subject_set.command()
@click.argument('subject-set-id', required=False, type=int)
@click.option(
    '--project-id',
    '-p',
    help="Show subject sets belonging to the given project.",
    required=False,
    type=int
)
@click.option(
    '--workflow-id',
    '-w',
    help="Show subject sets linked to the given workflow.",
    required=False,
    type=int
)
@click.option(
    '--quiet',
    '-q',
    help='Only print subject set IDs (omit names).',
    is_flag=True,
)
def ls(subject_set_id, project_id, workflow_id, quiet):
    """Lists subject set IDs and names"""

    if subject_set_id and not project_id and not workflow_id:
        subject_set = SubjectSet.find(subject_set_id)
        if quiet:
            click.echo(subject_set.id)
        else:
            echo_subject_set(subject_set)
        return

    args = {}
    if project_id:
        args['project_id'] = project_id
    if workflow_id:
        args['workflow_id'] = workflow_id
    if subject_set_id:
        args['subject_set_id'] = subject_set_id

    subject_sets = SubjectSet.where(**args)

    if quiet:
        click.echo(" ".join([s.id for s in subject_sets]))
    else:
        for subject_set in subject_sets:
            echo_subject_set(subject_set)


@subject_set.command()
@click.argument('subject-set-id', required=True)
def info(subject_set_id):
    subject_set = SubjectSet.find(subject_set_id)
    click.echo(yaml.dump(subject_set.raw))


@subject_set.command()
@click.option(
    '--quiet',
    '-q',
    help='Only print subject set ID (omit name).',
    is_flag=True,
)
@click.argument('project-id', required=True, type=int)
@click.argument('display-name', required=True)
def create(quiet, project_id, display_name):
    """
    Creates a new subject set.

    Prints the subject set ID and name of the new subject set.
    """

    subject_set = SubjectSet()
    subject_set.links.project = project_id
    subject_set.display_name = display_name
    subject_set.save()

    if quiet:
        click.echo(subject_set.id)
    else:
        echo_subject_set(subject_set)


@subject_set.command()
@click.argument('subject-set-id', required=True, type=int)
@click.option(
    '--display-name',
    '-n',
    help="Sets the subject set's public display name.",
    required=False
)
def modify(subject_set_id, display_name):
    """
    Changes the attributes of an existing subject set.

    Any attributes which are not specified are left unchanged.
    """
    subject_set = SubjectSet.find(subject_set_id)
    if display_name:
        subject_set.display_name = display_name
    subject_set.save()
    echo_subject_set(subject_set)


@subject_set.command(name='upload-subjects')
@click.argument('subject-set-id', required=True, type=int)
@click.argument('manifest-files', required=True, nargs=-1)
@click.option(
    '--allow-missing',
    '-M',
    help=("Do not abort when creating subjects with no media files."),
    is_flag=True,
)
@click.option(
    '--remote-location',
    '-r',
    help=(
        "Specify a field (by column number) in the manifest which contains a "
        "URL to a remote media location. Can be used more than once."
    ),
    multiple=True,
    type=int,
    required=False,
)
@click.option(
    '--mime-type',
    '-m',
    help=(
        "MIME type for remote media. Defaults to image/png. Can be used more "
        "than once, in which case types are mapped one to one with remote "
        "locations in the order they are given. Has no effect without "
        "--remote-location."
    ),
    type=str,
    required=False,
    default=('image/png',),
    multiple=True
)
@click.option(
    '--file-column',
    '-f',
    help=(
        "Specify a field (by column number) in the manifest which contains a "
        "local file to be uploaded. Can be used more than once. Disables auto-"
        "detection of filename columns."
    ),
    multiple=True,
    type=int,
    required=False,
)
def upload_subjects(
    subject_set_id,
    manifest_files,
    allow_missing,
    remote_location,
    mime_type,
    file_column,
):
    """
    Uploads subjects from each of the given MANIFEST_FILES.

    Example with only local files:

    $ panoptes subject-set upload-subjects 4667 manifest.csv

    Local filenames will be automatically detected in the manifest and
    uploaded, or filename columns can be specified with --file-column.

    If you are hosting your media yourself, you can put the URLs in the
    manifest and specify the column number(s):

    $ panoptes subject-set upload-subjects -r 1 4667 manifest.csv

    $ panoptes subject-set upload-subjects -r 1 -r 2 4667 manifest.csv

    Any local files will still be detected and uploaded.
    """
    if (
        len(manifest_files) > 1
        and any(map(lambda m: m.endswith('.yaml'), manifest_files))
    ):
        click.echo(
            'Error: YAML manifests must be processed one at a time.',
            err=True,
        )
        return -1
    elif manifest_files[0].endswith('.yaml'):
        with open(manifest_files[0], 'r') as yaml_manifest:
            upload_state = yaml.load(yaml_manifest, Loader=yaml.FullLoader)
        if upload_state['state_version'] > CURRENT_STATE_VERSION:
            click.echo(
                'Error: {} was generated by a newer version of the Panoptes '
                'CLI and is not compatible with this version.'.format(
                    manifest_files[0],
                ),
                err=True,
            )
            return -1
        if upload_state['subject_set_id'] != subject_set_id:
            click.echo(
                'Warning: You specified subject set {} but this YAML '
                'manifest is for subject set {}.'.format(
                    subject_set_id,
                    upload_state['subject_set_id'],
                ),
                err=True,
            )
            click.confirm(
                'Upload {} to subject set {} ({})?'.format(
                    manifest_files[0],
                    subject_set_id,
                    SubjectSet.find(subject_set_id).display_name,
                ),
                abort=True
            )
            upload_state['subject_set_id'] = subject_set_id
        resumed_upload = True
    else:
        upload_state = {
            'state_version': CURRENT_STATE_VERSION,
            'subject_set_id': subject_set_id,
            'manifest_files': manifest_files,
            'allow_missing': allow_missing,
            'remote_location': remote_location,
            'mime_type': mime_type,
            'file_column': file_column,
            'waiting_to_upload': [],
            'waiting_to_link': {},
        }
        resumed_upload = False

    remote_location_count = len(upload_state['remote_location'])
    mime_type_count = len(upload_state['mime_type'])
    if remote_location_count > 1 and mime_type_count == 1:
        upload_state['mime_type'] = (
            upload_state['mime_type'] * remote_location_count
        )
    elif remote_location_count > 0 and mime_type_count != remote_location_count:
        click.echo(
            'Error: The number of MIME types given must be either 1 or equal '
            'to the number of remote locations.',
            err=True,
        )
        return -1

    def validate_file(file_path):
        if not os.path.isfile(file_path):
            click.echo(
                'Error: File "{}" could not be found.'.format(
                    file_path,
                ),
                err=True,
            )
            return False

        file_size = os.path.getsize(file_path)
        if file_size == 0:
            click.echo(
                'Error: File "{}" is empty.'.format(
                    file_path,
                ),
                err=True,
            )
            return False
        elif file_size > MAX_UPLOAD_FILE_SIZE:
            click.echo(
                'Error: File "{}" is {}, larger than the maximum {}.'.format(
                    file_path,
                    humanize.naturalsize(file_size),
                    humanize.naturalsize(MAX_UPLOAD_FILE_SIZE),
                ),
                err=True,
            )
            return False
        return True

    def get_index_fields(headers):
        index_fields = [header.lstrip('%') for header in headers if header.startswith('%')]
        return ",".join(str(field) for field in index_fields)

    subject_set = SubjectSet.find(upload_state['subject_set_id'])
    if not resumed_upload:
        subject_rows = []
        for manifest_file in upload_state['manifest_files']:
            with open(manifest_file, 'U') as manifest_f:
                file_root = os.path.dirname(manifest_file)
                r = csv.reader(manifest_f, skipinitialspace=True)
                headers = next(r)
                # update set metadata for indexed sets
                index_fields = get_index_fields(headers)
                if index_fields:
                    subject_set.metadata['indexFields'] = index_fields
                    subject_set.save()
                # remove leading % from subject metadata headings
                cleaned_headers = [header.lstrip('%') for header in headers]
                for row in r:
                    metadata = dict(zip(cleaned_headers, row))
                    files = []
                    if not upload_state['file_column']:
                        upload_state['file_column'] = []
                        for field_number, col in enumerate(row, start=1):
                            file_path = os.path.join(file_root, col)
                            if os.path.exists(file_path):
                                upload_state['file_column'].append(
                                    field_number,
                                )
                                if validate_file(file_path):
                                    files.append(file_path)
                                elif not upload_state['allow_missing']:
                                    return -1
                    else:
                        for field_number in upload_state['file_column']:
                            file_path = os.path.join(
                                file_root,
                                row[field_number - 1]
                            )
                            if validate_file(file_path):
                                files.append(file_path)
                            elif not upload_state['allow_missing']:
                                return -1

                    for field_number, _mime_type in zip(
                        upload_state['remote_location'],
                        upload_state['mime_type'],
                    ):
                        files.append({_mime_type: row[field_number - 1]})

                    if len(files) == 0:
                        click.echo(
                            'Could not find any files in row:',
                            err=True,
                        )
                        click.echo(','.join(row), err=True)
                        if not upload_state['allow_missing']:
                            return -1
                        else:
                            continue
                    subject_rows.append((files, metadata))

                if not subject_rows:
                    click.echo(
                        'File {} did not contain any rows.'.format(
                            manifest_file,
                        ),
                        err=True,
                    )
                    return -1

        subject_rows = list(enumerate(subject_rows))
        upload_state['waiting_to_upload'] = copy.deepcopy(subject_rows)
    else:
        for subject_id, subject_row in upload_state['waiting_to_link'].items():
            try:
                subject = Subject.find(subject_id)
            except PanoptesAPIException:
                upload_state['waiting_to_upload'].append(subject_row)
                del upload_state['waiting_to_link'][subject_id]
        subject_rows = copy.deepcopy(upload_state['waiting_to_upload'])

    pending_subjects = []

    def move_created(limit):
        while len(pending_subjects) > limit:
            for subject, subject_row in pending_subjects:
                if subject.async_save_result:
                    pending_subjects.remove((subject, subject_row))
                    upload_state['waiting_to_upload'].remove(subject_row)
                    upload_state['waiting_to_link'][subject.id] = subject_row
            time.sleep(0.5)

    def link_subjects(limit):
        if len(upload_state['waiting_to_link']) > limit:
            subject_set.add(list(upload_state['waiting_to_link'].keys()))
            upload_state['waiting_to_link'].clear()

    with click.progressbar(
        subject_rows,
        length=len(subject_rows),
        label='Uploading subjects',
    ) as _subject_rows:
        try:
            with Subject.async_saves():
                for subject_row in _subject_rows:
                    count, (files, metadata) = subject_row
                    subject = Subject()
                    subject.links.project = subject_set.links.project
                    for media_file in files:
                        subject.add_location(media_file)
                    subject.metadata.update(metadata)
                    subject.save()

                    pending_subjects.append((subject, subject_row))

                    move_created(MAX_PENDING_SUBJECTS)
                    link_subjects(LINK_BATCH_SIZE)

            move_created(0)
            link_subjects(0)
        finally:
            if (
                len(pending_subjects) > 0
                or len(upload_state['waiting_to_link']) > 0
            ):
                click.echo('Error: Upload failed.', err=True)
                if click.confirm(
                    'Would you like to save the upload state to resume the '
                    'upload later?',
                    default=True,
                ):
                    while True:
                        state_file_name = 'panoptes-upload-{}.yaml'.format(
                            subject_set_id,
                        )
                        state_file_name = click.prompt(
                            'Enter filename to save to',
                            default=state_file_name,
                        )

                        if not state_file_name.endswith('.yaml'):
                            click.echo(
                                'Error: File name must end in ".yaml".',
                                err=True,
                            )
                            if click.confirm(
                                'Save to {}.yaml?'.format(state_file_name),
                                default=True,
                            ):
                                state_file_name += '.yaml'
                            else:
                                continue
                        if not is_valid_filename(state_file_name):
                            click.echo(
                                'Error: {} is not a valid file name'.format(
                                    state_file_name,
                                ),
                                err=True,
                            )
                            sanitized_filename = sanitize_filename(
                                state_file_name,
                            )
                            if click.confirm(
                                'Save to {}?'.format(
                                    sanitized_filename,
                                ),
                                default=True,
                            ):
                                state_file_name = sanitized_filename
                            else:
                                continue
                        if os.path.exists(state_file_name):
                            if not click.confirm(
                                'File {} already exists. Overwrite?'.format(
                                    state_file_name,
                                ),
                                default=False,
                            ):
                                continue
                        break

                    with open(state_file_name, 'w') as state_file:
                        yaml.dump(upload_state, state_file)


@subject_set.command(name='add-subjects')
@click.argument('subject-set-id', required=True, type=int)
@click.argument('subject-ids', required=False, nargs=-1)
@click.option(
    '--id-file',
    '-f',
    type=click.File('r'),
    help=(
        "Specify a filename which contains a list of subject IDs, one per line."
    ),
)
def add_subjects(subject_set_id, subject_ids, id_file):
    """
    Links existing subjects to this subject set.

    This command is useful mainly for adding previously uploaded subjects to
    additional subject sets.

    See the upload-subjects command to create new subjects in a subject set.
    """
    s = SubjectSet.find(subject_set_id)
    if id_file:
        s.add([l.strip() for l in id_file.readlines()])
    if subject_ids:
        s.add(subject_ids)


@subject_set.command(name='remove-subjects')
@click.argument('subject-set-id', required=True, type=int)
@click.argument('subject-ids', required=False, nargs=-1)
@click.option(
    '--id-file',
    '-f',
    type=click.File('r'),
    help=(
        "Specify a filename which contains a list of subject IDs, one per line."
    ),
)
def remove_subjects(subject_set_id, subject_ids, id_file):
    """
    Unlinks subjects from this subject set.

    The subjects themselves are not deleted or modified in any way and will
    still be present in any other sets they're linked to.
    """

    s = SubjectSet.find(subject_set_id)
    if id_file:
        s.remove([l.strip() for l in id_file.readlines()])
    if subject_ids:
        s.remove(subject_ids)


@subject_set.command()
@click.option(
    '--force',
    '-f',
    is_flag=True,
    help='Delete without asking for confirmation.',
)
@click.argument('subject-set-ids', required=True, nargs=-1, type=int)
def delete(force, subject_set_ids):
    for subject_set_id in subject_set_ids:
        subject_set = SubjectSet.find(subject_set_id)
        if not force:
            click.confirm(
                'Delete subject set {} ({})?'.format(
                    subject_set_id,
                    subject_set.display_name,
                ),
                abort=True,
            )
        subject_set.delete()


@subject_set.command(name="download-classifications")
@click.argument('subject-set-id', required=True, type=int)
@click.argument('output-file', required=True, type=click.File('wb'))
@click.option(
    '--generate',
    '-g',
    help="Generates a new export before downloading.",
    is_flag=True
)
@click.option(
    '--generate-timeout',
    '-T',
    help=(
        "Time in seconds to wait for new export to be ready. Defaults to "
        "unlimited. Has no effect unless --generate is given."
    ),
    required=False,
    type=int,
)
def download_classifications(
    subject_set_id,
    output_file,
    generate,
    generate_timeout
):
    """
    Downloads a subject-set specific classifications export for the given subject set.

    OUTPUT_FILE will be overwritten if it already exists. Set OUTPUT_FILE to -
    to output to stdout.
    """

    subject_set = SubjectSet.find(subject_set_id)

    if generate:
        click.echo("Generating new export...", err=True)

    export = subject_set.get_export(
        'classifications',
        generate=generate,
        wait_timeout=generate_timeout
    )

    with click.progressbar(
        export.iter_content(chunk_size=1024),
        label='Downloading',
        length=(int(export.headers.get('content-length')) / 1024 + 1),
        file=click.get_text_stream('stderr'),
    ) as chunks:
        for chunk in chunks:
            output_file.write(chunk)


def echo_subject_set(subject_set):
    click.echo(
        u'{} {}'.format(
            subject_set.id,
            subject_set.display_name
        )
    )


from panoptes_client import Subject
