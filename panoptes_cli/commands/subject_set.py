import click
import csv
import os
import re

from panoptes_cli.scripts.panoptes import cli
from panoptes_client import SubjectSet

IMAGE_REGEX = r'.*\.(png|jp(e)g|gif|svg)$'
LINK_BATCH_SIZE = 10

@cli.group()
def subject_set():
    pass

@subject_set.command()
@click.argument('subject-set-id', type=int)
def ls(subject_set_id):
    echo_subject_set(SubjectSet.find(subject_set_id))

@subject_set.command()
@click.option('--project-id', required=True, type=int)
@click.option('--display-name', required=True)
def create(project_id, display_name):
    subject_set = SubjectSet()
    subject_set.links.project = project_id
    subject_set.display_name = display_name
    subject_set.save()
    echo_subject_set(subject_set)

@subject_set.command()
@click.option('--subject-set-id', required=True, type=int)
@click.option('--project-id', required=False, type=int)
@click.option('--display-name', required=False)
def modify(subject_set_id, project_id, display_name):
    subject_set = SubjectSet.find(subject_set_id)
    if project_id:
        subject_set.links.project = project_id
    if display_name:
        subject_set.display_name = display_name
    subject_set.save()
    echo_subject_set(subject_set)

@subject_set.command()
@click.option('--subject-set-id', required=True, type=int)
@click.option('--manifest-file', required=True)
def upload_subjects(subject_set_id, manifest_file):
    subject_set = SubjectSet.find(subject_set_id)
    subject_rows = []
    with open(manifest_file) as manifest_f:
        file_root = os.path.dirname(manifest_file)
        r = csv.reader(manifest_f)
        headers = r.next()
        for row in r:
            metadata = dict(zip(headers, row))
            files = []
            for col in row:
                file_match = re.match(IMAGE_REGEX, col)
                file_path = os.path.join(file_root, col)
                if file_match and os.path.exists(file_path):
                    files.append(file_path)
            if len(files) == 0:
                click.echo('Could not find any files in row:', err=True)
                click.echo(','.join(row), err=True)
                return -1
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
            map(subject.add_location, files)
            subject.metadata.update(metadata)
            subject.save()
            created_subjects.append(subject)

            if (count + 1) % LINK_BATCH_SIZE == 0:
                subject_set.add_subjects(created_subjects)
                created_subjects = []

        if len(created_subjects) > 0:
            subject_set.add_subjects(created_subjects)

def echo_subject_set(subject_set):
    click.echo(
        u'{} {}'.format(
            subject_set.id,
            subject_set.display_name
        )
    )

from panoptes_client import Subject
