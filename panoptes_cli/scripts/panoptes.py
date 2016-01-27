import click
from panoptes_client.panoptes import Panoptes

@click.group()
@click.option(
    '--endpoint', default='https://panoptes.zooniverse.org/api', type=str
)
@click.pass_context
def cli(ctx, endpoint):
    ctx.panoptes = Panoptes(endpoint=endpoint)

from panoptes_cli.commands.project import *
from panoptes_cli.commands.subject import *
