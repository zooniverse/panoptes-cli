import csv
import yaml

import click

from panoptes_cli.scripts.panoptes import cli
from panoptes_client import Subject


@cli.group()
def subject():
    """Contains commands for managing subjects."""

    pass


@subject.command()
@click.option(
    "--subject-set-id",
    "-s",
    help="List subjects from the given subject set.",
    type=int,
    required=False,
)
@click.option(
    "--quiet",
    "-q",
    is_flag=True,
    help="Only print subject IDs (omit media URLs).",
)
@click.argument("subject-ids", type=int, required=False, nargs=-1)
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


@subject.command()
@click.argument("subject-id", required=True)
def info(subject_id):
    subject = Subject.find(subject_id)
    click.echo(yaml.dump(subject.raw))


@subject.command()
@click.option(
    "--force",
    "-f",
    is_flag=True,
    help="Delete without asking for confirmation.",
)
@click.argument("subject-ids", required=True, nargs=-1, type=int)
def delete(force, subject_ids):
    for subject_id in subject_ids:
        if not force:
            click.confirm("Delete subject {}?".format(subject_id), abort=True)
        Subject.find(subject_id).delete()


@subject.command()
@click.option(
    "--replace",
    "-r",
    is_flag=True,
    help="Replace all existing metadata rather than merging.",
)
@click.argument("metadata-file", required=True, nargs=1)
def update_metadata(replace, metadata_file):
    """
    Updates subject metadata from a CSV file.

    The CSV file should contain a "subject_id" column listing subject IDs.
    All other column names are taken to be metadata keys.
    """
    with open(metadata_file, "r") as metadata_f:
        total_tows = len(metadata_f.readlines())
        metadata_f.seek(0)
        metadata_rows = csv.DictReader(metadata_f)
        with click.progressbar(
            metadata_rows,
            length=total_tows,
            label="Update subject metadata",
        ) as _metadata_rows:
            for metadata in _metadata_rows:
                subject_id = metadata.pop("subject_id")
                try:
                    subject = Subject.find(subject_id)
                    if replace:
                        subject.metadata = dict(metadata)
                    else:
                        subject.metadata.update(metadata)
                    subject.save()
                except Exception as e:
                    click.echo(f"Failed to update subject {subject_id}: {e}", err=True)


def echo_subject(subject):
    m = map(lambda l: list(l.values())[0], subject.locations)
    click.echo("{} {}".format(subject.id, " ".join(m)))
