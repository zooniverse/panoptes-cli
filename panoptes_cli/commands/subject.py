import click

from panoptes_cli.scripts.panoptes import cli
from panoptes_client import Subject

@cli.group()
def subject():
    """Contains commands for retrieving information about subjects."""

    pass

@subject.command()
@click.option(
    '--subject-set-id',
    '-s',
    help="List subjects from the given subject set.",
    type=int,
    required=False
)
@click.option(
    '--quiet',
    '-q',
    is_flag=True,
    help='Only print subject IDs (omit media URLs).',
)
@click.argument('subject-ids', type=int, required=False, nargs=-1)
def ls(subject_set_id, quiet, subject_ids):
    """
    Lists subject IDs and their media URLs.
    """

    if subject_ids:
        for subject_id in subject_ids:
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
            ' '.join(map(lambda l: list(l.values())[0], subject.locations))
        )
    )
