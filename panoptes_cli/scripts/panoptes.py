import click
import os
import yaml
from panoptes_client import Panoptes

@click.group()
@click.option(
    '--endpoint', type=str
)
@click.pass_context
def cli(ctx, endpoint):
    ctx.config_dir = os.path.join(os.environ['HOME'], '.panoptes')
    ctx.config_file = os.path.join(ctx.config_dir, 'config.yml')
    ctx.config = {
        'endpoint': 'https://panoptes.zooniverse.org',
        'username': '',
        'password': '',
    }

    try:
        with open(ctx.config_file) as conf_f:
            ctx.config.update(yaml.load(conf_f))
    except IOError:
        pass

    if endpoint:
        ctx.config['endpoint'] = endpoint

    Panoptes.connect(
        endpoint=ctx.config['endpoint'],
        username=ctx.config['username'],
        password=ctx.config['password']
    )

from panoptes_cli.commands.configure import *
from panoptes_cli.commands.project import *
from panoptes_cli.commands.subject import *
from panoptes_cli.commands.subject_set import *
