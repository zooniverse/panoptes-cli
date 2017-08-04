import click

from panoptes_cli.scripts.panoptes import cli
from panoptes_client import Project

@cli.group()
def project():
    pass

@project.command()
@click.option('--project-id', '-p', required=False, type=int)
@click.option('--display-name', '-n')
@click.option('--launch-approved', '-a', is_flag=True)
@click.option('--slug', '-s')
@click.option(
    '--quiet',
    '-q',
    is_flag=True,
    help='Only print project IDs',
)
@click.argument('search', required=False, nargs=-1)
def ls(project_id, display_name, launch_approved, slug, quiet, search):
    if not launch_approved:
        launch_approved = None

    projects = Project.where(
        id=project_id,
        slug=slug,
        display_name=display_name,
        launch_approved=launch_approved,
        search=" ".join(search)
    )

    if quiet:
        click.echo(" ".join([p.id for p in projects]))
    else:
        for project in projects:
            echo_project(project)

@project.command()
@click.argument('display-name', required=True)
@click.argument('description', required=True)
@click.option('--primary-language', '-l', default='en')
@click.option('--public', '-p', is_flag=True)
def create(display_name, description, primary_language, public):
    project = Project()
    project.display_name = display_name
    project.description = description
    project.primary_language = primary_language
    project.private = not public
    project.save()
    echo_project(project)

@project.command()
@click.argument('project-id', required=True, type=int)
@click.option('--display-name', '-n', required=False)
@click.option('--description', '-d', required=False)
@click.option('--primary-language', '-l', default='en')
@click.option('--public', '-p', is_flag=True)
def modify(project_id, display_name, description, primary_language, public):
    project = Project.find(project_id)
    if display_name:
        project.display_name = display_name
    if description:
        project.description = description
    if primary_language:
        project.primary_language = primary_language
    if private is not None:
        project.private = not public
    project.save()
    echo_project(project)

@project.command()
@click.argument('project-id', required=True, type=int)
@click.argument('output-file', required=True, type=click.File('wb'))
@click.option('--generate', '-g', is_flag=True)
@click.option(
    '--generate-timeout',
    '-T',
    required=False,
    type=int,
)
@click.option(
    '--data-type',
    '-t',
    type=click.Choice([
        'classifications',
        'subjects',
        'workflows',
        'workflow_contents',
        'talk_comments',
        'talk_tags']),
    default='classifications'
)
def download(project_id, output_file, generate, generate_timeout, data_type):
    project = Project.find(project_id)
    export = project.get_export(
        data_type,
        generate=generate,
        wait_timeout=generate_timeout
    )
    for chunk in export.iter_content():
        output_file.write(chunk)

def echo_project(project):
    click.echo(
        u'{}{} {} {}'.format(
            '*' if project.private else '',
            project.id,
            project.slug,
            project.display_name)
    )
