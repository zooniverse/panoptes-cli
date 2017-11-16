import click
import os
import yaml

from panoptes_cli.scripts.panoptes import cli

@cli.command()
@click.pass_context
def configure(ctx):
    """Sets default values for configuration options."""

    if not os.path.isdir(ctx.parent.config_dir):
        os.mkdir(ctx.parent.config_dir)

    for opt, value in ctx.parent.config.items():
        ctx.parent.config[opt] = click.prompt(
            opt,
            default=value
        )

    with open(ctx.parent.config_file, 'w') as conf_f:
        yaml.dump(ctx.parent.config, conf_f, default_flow_style=False)
