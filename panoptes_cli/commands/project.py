import click

from panoptes_cli.scripts.panoptes import cli
from panoptes_client.project import Project

@cli.group()
@click.pass_context
def project(ctx):
    pass

@project.command()
@click.option('--id', help='Project ID', required=False, type=int)
@click.option('--display-name')
@click.argument('slug', required=False)
@click.pass_context
def ls(ctx, id, display_name, slug):
    projects = Project.find(id, slug=slug, display_name=display_name)

    for project in projects:
        click.echo(project)
