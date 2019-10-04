import csv
import os
import re
import sys
import time
import yaml

import click
import humanize

from panoptes_cli.scripts.panoptes import cli
from panoptes_client import SubjectSet
from panoptes_client.panoptes import PanoptesAPIException

LINK_BATCH_SIZE = 10
MAX_PENDING_SUBJECTS = 50
MAX_UPLOAD_FILE_SIZE = 1024 * 1024


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
@click.argument('project-id', required=True, type=int)
@click.argument('display-name', required=True)
def create(project_id, display_name):
    """
    Creates a new subject set.

    Prints the subject set ID and name of the new subject set.
    """

    subject_set = SubjectSet()
    subject_set.links.project = project_id
    subject_set.display_name = display_name
    subject_set.save()
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

    remote_location_count = len(remote_location)
    mime_type_count = len(mime_type)
    if remote_location_count > 1 and mime_type_count == 1:
        mime_type = mime_type * remote_location_count
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

    subject_set = SubjectSet.find(subject_set_id)
    subject_rows = []
    for manifest_file in manifest_files:
        with open(manifest_file, 'U') as manifest_f:
            file_root = os.path.dirname(manifest_file)
            r = csv.reader(manifest_f)
            headers = next(r)
            for row in r:
                metadata = dict(zip(headers, row))
                files = []
                if not file_column:
                    file_column = []
                    for field_number, col in enumerate(row, start=1):
                        file_path = os.path.join(file_root, col)
                        if os.path.exists(file_path):
                            file_column.append(field_number)
                            if not validate_file(file_path):
                                return -1
                            files.append(file_path)
                else:
                    for field_number in file_column:
                        file_path = os.path.join(
                            file_root,
                            row[field_number - 1]
                        )
                        if not validate_file(file_path):
                            return -1
                        files.append(file_path)

                for field_number, _mime_type in zip(remote_location, mime_type):
                    files.append({_mime_type: row[field_number - 1]})

                if len(files) == 0:
                    click.echo('Could not find any files in row:', err=True)
                    click.echo(','.join(row), err=True)
                    if not allow_missing:
                        return -1
                    else:
                        continue
                subject_rows.append((files, metadata))

            if not subject_rows:
                click.echo(
                    'File {} did not contain any rows.'.format(manifest_file),
                    err=True,
                )
                return -1

    created_subjects = []
    pending_subjects = []

    def move_created(limit):
        while len(pending_subjects) > limit:
            for subject in pending_subjects:
                if subject.async_save_result:
                    created_subjects.append(subject)
                    pending_subjects.remove(subject)
            time.sleep(0.5)

    def link_created(limit):
        if len(created_subjects) > limit:
            subject_set.add(created_subjects)
            del created_subjects[:]

    with click.progressbar(
        enumerate(subject_rows),
        length=len(subject_rows),
        label='Uploading subjects',
    ) as _subject_rows:
        with Subject.async_saves():
            for count, (files, metadata) in _subject_rows:
                subject = Subject()
                subject.links.project = subject_set.links.project
                for media_file in files:
                    subject.add_location(media_file)
                subject.metadata.update(metadata)
                subject.save()

                pending_subjects.append(subject)

                move_created(MAX_PENDING_SUBJECTS)
                link_created(LINK_BATCH_SIZE)

        move_created(0)
        link_created(0)


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


def echo_subject_set(subject_set):
    click.echo(
        u'{} {}'.format(
            subject_set.id,
            subject_set.display_name
        )
    )


from panoptes_client import Subject