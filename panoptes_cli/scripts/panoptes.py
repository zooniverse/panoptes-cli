import os

import click
import keyring
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
    }

    try:
        with open(ctx.config_file) as conf_f:
            ctx.config.update(yaml.full_load(conf_f))
    except IOError:
        pass

    if endpoint:
        ctx.config['endpoint'] = endpoint

    if ctx.invoked_subcommand != 'configure':
        try:
            password = keyring.get_password('panoptes', ctx.config['username'])
        except RuntimeError:
            password = None

        if 'password' in ctx.config:
            if not password:
                try:
                    password = ctx.config['password']
                    keyring.set_password(
                        'panoptes',
                        ctx.config['username'],
                        password,
                    )
                    retrieved_password = keyring.get_password(
                        'panoptes', 
                        ctx.config['username'],
                    )

                    del ctx.config['password']
                    save_config(ctx.config_file, ctx.config)
                except RuntimeError:
                    click.echo(
                        'Warning: Your password is stored insecurely and '
                        'secure keyrings are not supported on your system.',
                        err=True,
                    )

        if not password:
            password = click.prompt(
                'Password for {}'.format(ctx.config['username']),
                hide_input=True,
            )

        Panoptes.connect(
            endpoint=ctx.config['endpoint'],
            username=ctx.config['username'],
            password=password,
            admin=admin,
        )

from panoptes_cli.commands.configure import *
from panoptes_cli.commands.info import *
from panoptes_cli.commands.project import *
from panoptes_cli.commands.subject import *
from panoptes_cli.commands.subject_set import *
from panoptes_cli.commands.user import *
from panoptes_cli.commands.workflow import *
