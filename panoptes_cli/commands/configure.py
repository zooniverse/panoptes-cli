import os

import click
import keyring
import yaml

from panoptes_cli.scripts.panoptes import cli

@cli.command()
@click.pass_context
@click.option(
    '--edit-all',
    '-a',
    help=(
        "Modify all configuration options (rather than just username and "
        "password)."
    ),
    is_flag=True
)
def configure(ctx, edit_all):
    """Sets default values for configuration options."""

    if not os.path.isdir(ctx.parent.config_dir):
        os.mkdir(ctx.parent.config_dir)

    for opt, value in ctx.parent.config.items():
        if opt == 'endpoint' and not edit_all:
            continue

        ctx.parent.config[opt] = click.prompt(
            opt,
            default=value,
        )

    if not ctx.parent.config['endpoint'].startswith('https://'):
        click.echo(
            'Error: Invalid endpoint supplied. Endpoint must be an HTTPS URL.'
        )
        return -1
    
    new_password = click.prompt(
        'Password [leave blank for no change]',
        hide_input=True,
        show_default=False,
        default='',
    )
    if new_password:
        try:
            keyring.set_password(
                'panoptes',
                ctx.parent.config['username'],
                new_password,
            )
        except RuntimeError:
            click.echo(
                'Warning: Could not save your password to the keyring. '
                'You will be asked for your password each time.',
                err=True,
            )

    save_config(ctx.parent.config_file, ctx.parent.config)


def save_config(config_file, config):
    with open(config_file, 'w') as conf_f:
        yaml.dump(config, conf_f, default_flow_style=False)