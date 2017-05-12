import click

from panoptes_cli.scripts.panoptes import cli
from panoptes_client import Subject

@cli.group()
def subject():
    pass

@subject.command()
@click.option('--subject-set-id', type=int, required=False)
@click.option(
    '--quiet',
    '-q',
    is_flag=True,
    help='Only print subject IDs',
)
@click.argument('subject-id', type=int, required=False)
def ls(subject_set_id, quiet, subject_id):
    if subject_id:
        subject = Subject.find(subject_id)
        if quiet:
            click.echo(subject.id)
        else:
            echo_subject(subject)
        return

    subjects = Subject.where(subject_set_id=subject_set_id)
    if quiet:
        click.echo(" ".join([s.id for s in subjects]))
    else:
        for subject in subjects:
            echo_subject(subject)


def echo_subject(subject):
    click.echo(
        u'{} {}'.format(
            subject.id,
            ' '.join(map(lambda l: l.values()[0], subject.locations))
        )
    )
