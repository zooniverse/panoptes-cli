import platform

import click
import pkg_resources

from panoptes_cli.scripts.panoptes import cli


@cli.command()
@click.pass_context
def info(ctx):
    """Displays version and environment information for debugging."""

    info = {
        'Panoptes CLI version': (
            pkg_resources.require("panoptescli")[0].version
        ),
        'Panoptes client version': (
            pkg_resources.require("panoptes_client")[0].version
        ),
        'Operating system': '{} {}'.format(
            platform.system(),
            platform.release(),
        ),
        'API endpoint': ctx.parent.config['endpoint'],
        'Click': pkg_resources.require("click")[0].version,
        'PyYAML': pkg_resources.require("PyYAML")[0].version,
        'Python version': platform.python_version(),
    }

    try:
        info['libmagic'] = pkg_resources.require("python-magic")[0].version
    except pkg_resources.DistributionNotFound:
        info['libmagic'] = False

    for k, v in info.items():
        click.echo('{}: {}'.format(k, v))
