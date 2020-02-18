import yaml

import click

from panoptes_cli.scripts.panoptes import cli
from panoptes_client import Project

@cli.group()
def project():
    """Contains commands for managing projects."""
    pass

@project.command()
@click.option(
    '--project-id',
    '-p',
    help="Show the project with the given ID.",
    required=False,
    type=int,
)
@click.option(
    '--display-name',
    '-n',
    help="Show projects whose display name exactly matches the given string.",
)
@click.option(
    '--launch-approved',
    '-a',
    help="Only show projects which have been approved by the Zooniverse.",
    is_flag=True
)
@click.option(
    '--slug',
    '-s',
    help="Show the project whose slug exactly matches the given string.",
)
@click.option(
    '--quiet',
    '-q',
    is_flag=True,
    help='Only print project IDs (omit project names).',
)
@click.argument(
    'search',
    required=False,
    nargs=-1
)
def ls(project_id, display_name, launch_approved, slug, quiet, search):
    """
    Lists project IDs and names.

    Any given SEARCH terms are used for a full-text search of project titles.

    A "*" before the project ID indicates that the project is private.
    """

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
@click.argument('project-id', required=True)
def info(project_id):
    project = Project.find(project_id)
    click.echo(yaml.dump(project.raw))


@project.command()
@click.argument('display-name', required=True)
@click.argument('description', required=True)
@click.option(
    '--primary-language',
    '-l',
    help="Sets the language code for the project's primary language.",
    default='en'
)
@click.option(
    '--public',
    '-p',
    help="Makes the project publically accessible.",
    is_flag=True
)
@click.option(
    '--quiet',
    '-q',
    help='Only print project ID (omit name).',
    is_flag=True,
)
def create(display_name, description, primary_language, public, quiet):
    """
    Creates a new project.

    Prints the project ID and name of the new project.
    """

    project = Project()
    project.display_name = display_name
    project.description = description
    project.primary_language = primary_language
    project.private = not public
    project.save()

    if quiet:
        click.echo(project.id)
    else:
        echo_project(project)

@project.command()
@click.argument('project-id', required=True, type=int)
@click.option(
    '--display-name',
    '-n',
    help="Sets the project's public display name.",
    required=False,
)
@click.option(
    '--description',
    '-d',
    help="Sets the full-text description of the project.",
    required=False,
)
@click.option(
    '--primary-language',
    '-l',
    help="Sets the language code for the project's primary language.",
    default='en',
)
@click.option(
    '--public/--private',
    '-p/-P',
    help="Sets the project to be public or private.",
    default=None,
)
def modify(project_id, display_name, description, primary_language, public):
    """
    Changes the attributes of an existing project.

    Any attributes which are not specified are left unchanged.
    """

    project = Project.find(project_id)
    if display_name:
        project.display_name = display_name
    if description:
        project.description = description
    if primary_language:
        project.primary_language = primary_language
    if public is not None:
        project.private = not public
    project.save()
    echo_project(project)

@project.command()
@click.argument('project-id', required=True, type=int)
@click.argument('output-file', required=True, type=click.File('wb'))
@click.option(
    '--generate',
    '-g',
    help="Generates a new export before downloading.",
    is_flag=True
)
@click.option(
    '--generate-timeout',
    '-T',
    help=(
        "Time in seconds to wait for new export to be ready. Defaults to "
        "unlimited. Has no effect unless --generate is given."
    ),
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
    """
    Downloads project-level data exports.

    OUTPUT_FILE will be overwritten if it already exists. Set OUTPUT_FILE to -
    to output to stdout.
    """

    project = Project.find(project_id)

    if generate:
        click.echo("Generating new export...", err=True)

    export = project.get_export(
        data_type,
        generate=generate,
        wait_timeout=generate_timeout
    )

    with click.progressbar(
        export.iter_content(chunk_size=1024),
        label='Downloading',
        length=(int(export.headers.get('content-length')) / 1024 + 1),
        file=click.get_text_stream('stderr'),
    ) as chunks:
        for chunk in chunks:
            output_file.write(chunk)


@project.command()
@click.option(
    '--force',
    '-f',
    is_flag=True,
    help='Delete without asking for confirmation.',
)
@click.argument('project-ids', required=True, nargs=-1, type=int)
def delete(force, project_ids):
    for project_id in project_ids:
        project = Project.find(project_id)
        if not force:
            click.confirm(
                'Delete project {} ({})?'.format(
                    project_id,
                    project.display_name,
                ),
                abort=True,
            )
        project.delete()


def echo_project(project):
    click.echo(
        u'{}{} {} {}'.format(
            '*' if project.private else '',
            project.id,
            project.slug,
            project.display_name)
    )
