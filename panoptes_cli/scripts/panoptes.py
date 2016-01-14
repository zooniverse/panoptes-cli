import click
from panoptes_client.panoptes import Panoptes

panoptes = Panoptes('https://panoptes.zooniverse.org/api')

@click.group()
def cli():
    pass

@cli.command()
@click.option('--id', help='Project ID', required=False, type=int)
@click.option('--display-name')
@click.argument('slug', required=False)
def project(id, display_name, slug):
    projects = panoptes.get_projects(id, slug=slug, display_name=display_name)

    for proj_data in projects['projects']:
        click.echo('Project name: %s' % proj_data['display_name'])
        click.echo('\tClassification count: %s' % proj_data['classifications_count'])
        click.echo('\tSubject count: %s' % proj_data['subjects_count'])
        click.echo('')

@cli.command()
@click.argument('subject_id', required=True)
def subject(subject_id):
    subject = panoptes.get_subject(subject_id)['subjects'][0]
    project = panoptes.get_project(subject['links']['project'])

    click.echo('Project: %s' % project['display_name'])

    click.echo('Locations:')

    for location in subject['locations']:
        for mimetype, uri in location.items():
            click.echo('\t%s: %s' % (mimetype, uri))
