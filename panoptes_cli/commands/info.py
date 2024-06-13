import platform

import click
import importlib.metadata

from panoptes_cli.scripts.panoptes import cli


@cli.command()
@click.pass_context
def info(ctx):
    """Displays version and environment information for debugging."""

    info = {
        'Panoptes CLI version': (
            importlib.metadata.version("panoptescli")
        ),
        'Panoptes client version': (
            importlib.metadata.version("panoptes_client")
        ),
        'Operating system': '{} {}'.format(
            platform.system(),
            platform.release(),
        ),
        'Python version': platform.python_version(),
        'API endpoint': ctx.parent.config['endpoint'],
        'Click': importlib.metadata.version("click"),
        'PyYAML': importlib.metadata.version("pyyaml"),
        'requests': importlib.metadata.version("requests"),
        'urllib3': importlib.metadata.version("urllib3")
    }

    try:
        info['libmagic'] = importlib.metadata.version("python-magic")
    except importlib.metadata.PackageNotFoundError:
        info['libmagic'] = False

    for k, v in info.items():
        click.echo('{}: {}'.format(k, v))
