import click

from panoptes_cli.scripts.panoptes import cli
from panoptes_client import Subject

@cli.group()
def subject():
    pass

@subject.command()
@click.argument('subject-id', type=int)
def ls(subject_id):
    echo_subject(Subject.find(subject_id))

def echo_subject(subject):
    click.echo(
        u'Subject {}:\n{}'.format(
            subject.id,
            '\n'.join(map(lambda l: l.values()[0], subject.locations))
        )
    )
