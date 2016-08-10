import click

from panoptes_cli.scripts.panoptes import cli
from panoptes_client import Project

@cli.group()
def project():
    pass

@project.command()
@click.option('--project-id', required=False, type=int)
@click.option('--display-name')
@click.option('--launch-approved', is_flag=True)
@click.argument('slug', required=False)
def ls(project_id, display_name, launch_approved, slug):
    if not launch_approved:
        launch_approved = None

    projects = Project.where(
        id=project_id,
        slug=slug,
        display_name=display_name,
        launch_approved=launch_approved
    )

    for project in projects:
        echo_project(project)

@project.command()
@click.option('--display-name', required=True)
@click.option('--description', required=True)
@click.option('--primary-language', default='en')
@click.option('--private/--public', default=True)
def create(display_name, description, primary_language, private):
    project = Project()
    project.display_name = display_name
    project.description = description
    project.primary_language = primary_language
    project.private = private
    project.save()
    echo_project(project)

@project.command()
@click.option('--project-id', required=True, type=int)
@click.option('--display-name', required=False)
@click.option('--description', required=False)
@click.option('--primary-language', default='en')
@click.option('--private/--public', required=False)
def modify(project_id, display_name, description, primary_language, private):
    project = Project.find(project_id)
    if display_name:
        project.display_name = display_name
    if description:
        project.description = description
    if primary_language:
        project.primary_language = primary_language
    if private is not None:
        project.private = private
    project.save()
    echo_project(project)

@project.command()
@click.option('--project-id', required=True, type=int)
@click.option('--output', required=True, type=click.File('wb'))
@click.option('--generate/--no-generate', required=False)
@click.option('--generate-timeout', required=False, type=int, default=300)
def download_classifications(project_id, output, generate, generate_timeout):
    project = Project.find(project_id)
    export = project.get_classifications_export(
        generate=generate,
        wait_timeout=generate_timeout
    )
    for chunk in export.iter_content():
        output.write(chunk)

def echo_project(project):
    click.echo(
        u'{}{} {} {}'.format(
            '*' if project.private else '',
            project.id,
            project.slug,
            project.display_name)
    )
