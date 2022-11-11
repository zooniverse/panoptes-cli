import click

from panoptes_cli.scripts.panoptes import cli
from panoptes_client import Inaturalist


@cli.group()
def inaturalist():
    """Contains commands related to iNaturalist integration"""
    pass


@inaturalist.command(name='import-observations')
@click.option(
    '--taxon-id',
    help=(
        "iNaturalist Taxon ID of the taxa you want to import."
    ),
    required=True,
    type=int,
)
@click.option(
    '--subject-set-id',
    help=(
        "ID of the Zooniverse subject set to import into."
    ),
    required=True,
    type=int,
)
def import_observations(taxon_id, subject_set_id):
    """Requests Panoptes begin an iNaturalist subject import."""

    click.echo(f'Importing taxon ID {taxon_id} into subject set {subject_set_id}.')
    Inaturalist.inat_import(taxon_id, subject_set_id)

