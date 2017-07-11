import click
import csv
import os
import re

from panoptes_cli.scripts.panoptes import cli
from panoptes_client import SubjectSet

IMAGE_REGEX = r'.*\.(png|jpe?g|gif|svg)$'
LINK_BATCH_SIZE = 10


@cli.group(name='subject-set')
def subject_set():
    pass


@subject_set.command()
@click.argument('subject-set-id', required=False, type=int)
@click.option('--project-id', '-p', required=False, type=int)
@click.option('--workflow-id', '-w', required=False, type=int)
@click.option(
    '--quiet',
    '-q',
    is_flag=True,
    help='Only print subject set IDs',
)
def ls(subject_set_id, project_id, workflow_id, quiet):
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
@click.argument('project-id', required=True, type=int)
@click.argument('display-name', required=True)
def create(project_id, display_name):
    subject_set = SubjectSet()
    subject_set.links.project = project_id
    subject_set.display_name = display_name
    subject_set.save()
    echo_subject_set(subject_set)


@subject_set.command()
@click.argument('subject-set-id', required=True, type=int)
@click.option('--project-id', '-p', required=False, type=int)
@click.option('--display-name', '-n', required=False)
def modify(subject_set_id, project_id, display_name):
    subject_set = SubjectSet.find(subject_set_id)
    if project_id:
        subject_set.links.project = project_id
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
    help=("Specify a field in the manifest which contains a URL to a remote "
          "media location. Can be used more than once."),
    multiple=True,
    type=int,
    required=False,
)
@click.option(
    '--mime-type',
    '-m',
    help=("MIME type for remote media. Defaults to image/png."),
    type=str,
    required=False,
    default='image/png',
)
def upload_subjects(
    subject_set_id,
    manifest_files,
    allow_missing,
    remote_location,
    mime_type,
):
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
                for col in row:
                    file_match = re.match(IMAGE_REGEX, col)
                    file_path = os.path.join(file_root, col)
                    if file_match and os.path.exists(file_path):
                        files.append(file_path)

                for field_number in remote_location:
                    files.append({mime_type: row[field_number - 1]})

                if len(files) == 0:
                    click.echo('Could not find any files in row:', err=True)
                    click.echo(','.join(row), err=True)
                    if not allow_missing:
                        return -1
                    else:
                        continue
                subject_rows.append((files, metadata))

    created_subjects = []
    with click.progressbar(
        enumerate(subject_rows),
        length=len(subject_rows),
        label='Uploading subjects',
    ) as _subject_rows:
        for count, (files, metadata) in _subject_rows:
            subject = Subject()
            subject.links.project = subject_set.links.project
            for media_file in files:
                subject.add_location(media_file)
            subject.metadata.update(metadata)
            subject.save()
            created_subjects.append(subject)

            if (count + 1) % LINK_BATCH_SIZE == 0:
                subject_set.add(created_subjects)
                created_subjects = []

        if len(created_subjects) > 0:
            subject_set.add(created_subjects)


@subject_set.command(name='add-subjects')
@click.argument('subject-set-id', required=True, type=int)
@click.argument('subject-ids', required=True, nargs=-1)
def add_subjects(subject_set_id, subject_ids):
    s = SubjectSet.find(subject_set_id)
    s.add(subject_ids)


@subject_set.command(name='remove-subjects')
@click.argument('subject-set-id', required=True, type=int)
@click.argument('subject-ids', required=True, nargs=-1)
def remove_subjects(subject_set_id, subject_ids):
    s = SubjectSet.find(subject_set_id)
    s.remove(subject_ids)


def echo_subject_set(subject_set):
    click.echo(
        u'{} {}'.format(
            subject_set.id,
            subject_set.display_name
        )
    )

from panoptes_client import Subject
