import click
from panoptes_client.panoptes import Panoptes

panoptes = Panoptes('https://panoptes.zooniverse.org/api')

@click.group()
def cli():
    pass

@cli.command()
@click.option('--id', help='Project ID', required=False, type=int)
@click.option('--display-name')
@click.option('--sets', is_flag=True)
@click.argument('slug', required=False)
def project(id, display_name, slug, sets):
    projects = panoptes.get_projects(id, slug=slug, display_name=display_name)

    for proj_data in projects['projects']:
        click.echo('Project name: %s' % proj_data['display_name'])
        click.echo('\tClassification count: %s' % proj_data['classifications_count'])
        click.echo('\tSubject count: %s' % proj_data['subjects_count'])
        click.echo('')

        if sets or verbose:
            click.echo('Subject sets:')

            subject_sets = map(lambda id: panoptes.get_subject_set(id)['subject_sets'][0], proj_data['links']['subject_sets'])

            for subject_set in subject_sets:
                click.echo('\t%s: %s' % (subject_set['id'], subject_set['display_name']))

            click.echo('')

@cli.command()
@click.argument('subject_id', required=True, type=int)
def subject(subject_id):
    subject = panoptes.get_subject(subject_id)['subjects'][0]
    project = panoptes.get_project(subject['links']['project'])

    click.echo('Project: %s' % project['display_name'])

    click.echo('Locations:')

    for location in subject['locations']:
        for mimetype, uri in location.items():
            click.echo('\t%s: %s' % (mimetype, uri))
