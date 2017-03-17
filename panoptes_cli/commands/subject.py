import click

from panoptes_cli.scripts.panoptes import cli
from panoptes_client import Subject

@cli.group()
def subject():
    pass

@subject.command()
@click.option('--subject-set-id', type=int, required=False)
@click.argument('subject-id', type=int, required=False)
def ls(subject_set_id, subject_id):
    if subject_id:
        echo_subject(Subject.find(subject_id))
        return

    map(echo_subject, Subject.where(subject_set_id=subject_set_id))


def echo_subject(subject):
    click.echo(
        u'{} {}'.format(
            subject.id,
            ' '.join(map(lambda l: l.values()[0], subject.locations))
        )
    )
