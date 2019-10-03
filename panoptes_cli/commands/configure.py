import click
import os
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

        is_password = opt == 'password'
        ctx.parent.config[opt] = click.prompt(
            opt,
            default=value,
            hide_input=is_password,
            show_default=not is_password,
        )

    if not ctx.parent.config['endpoint'].startswith('https://'):
        click.echo(
            'Error: Invalid endpoint supplied. Endpoint must be an HTTPS URL.'
        )
        return -1

    with open(ctx.parent.config_file, 'w') as conf_f:
        yaml.dump(ctx.parent.config, conf_f, default_flow_style=False)
