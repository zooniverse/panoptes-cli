import click
import os
import yaml
from panoptes_client import Panoptes


@click.version_option(prog_name='Panoptes CLI')
@click.group()
@click.option(
    '--endpoint',
    '-e',
    help="Overides the default API endpoint",
    type=str,
)
@click.option(
    '--admin',
    '-a',
    help=(
        "Enables admin mode. Ignored if you're not logged in as an "
        "administrator."
    ),
    is_flag=True,
)
@click.pass_context
def cli(ctx, endpoint, admin):
    ctx.config_dir = os.path.expanduser('~/.panoptes/')
    ctx.config_file = os.path.join(ctx.config_dir, 'config.yml')
    ctx.config = {
        'endpoint': 'https://www.zooniverse.org',
        'username': '',
        'password': '',
    }

    try:
        with open(ctx.config_file) as conf_f:
            ctx.config.update(yaml.full_load(conf_f))
    except IOError:
        pass

    if endpoint:
        ctx.config['endpoint'] = endpoint

    if ctx.invoked_subcommand != 'configure':
        Panoptes.connect(
            endpoint=ctx.config['endpoint'],
            username=ctx.config['username'],
            password=ctx.config['password'],
            admin=admin,
        )

from panoptes_cli.commands.configure import *
from panoptes_cli.commands.info import *
from panoptes_cli.commands.project import *
from panoptes_cli.commands.subject import *
from panoptes_cli.commands.subject_set import *
from panoptes_cli.commands.user import *
from panoptes_cli.commands.workflow import *
from panoptes_cli.commands.inaturalist import *
