import click

from panoptes_cli.scripts.panoptes import cli
from panoptes_client import SubjectSet

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

def echo_subject_set(subject_set):
    click.echo(
        u'{} {}'.format(
            subject_set.id,
            subject_set.display_name
        )
    )
