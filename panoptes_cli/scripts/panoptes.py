import click
from panoptes_client.panoptes import Panoptes

panoptes = None

@click.group()
@click.option(
    '--endpoint', default='https://panoptes.zooniverse.org/api', type=str
)
def cli(endpoint):
    global panoptes
    panoptes = Panoptes(endpoint=endpoint)

@cli.command()
@click.option('--id', help='Project ID', required=False, type=int)
@click.option('--display-name')
@click.option('--sets', is_flag=True)
@click.option('--roles', is_flag=True)
@click.option('--verbose', '-v', is_flag=True)
@click.argument('slug', required=False)
def project(id, display_name, slug, sets, roles, verbose):
    projects = panoptes.get_projects(id, slug=slug, display_name=display_name)

    for proj_data in projects['projects']:
        click.echo(
            'Project: %s (ID: %s)' % (
                proj_data['display_name'], proj_data['id']
            )
        )
        click.echo(
            '\tClassification count: %s' % proj_data['classifications_count']
        )
        click.echo('\tSubject count: %s' % proj_data['subjects_count'])
        click.echo('')

        if sets or verbose:
            click.echo('Subject sets:')

            subject_sets = map(
                lambda id: panoptes.get_subject_set(id)['subject_sets'][0],
                proj_data['links']['subject_sets']
            )

            for subject_set in subject_sets:
                click.echo('\t%(id)s: %(display_name)s' % subject_set)

            click.echo('')

        if roles or verbose:
            click.echo('Roles:')

            def get_collaborator(role_id):
                role_data = panoptes.get_project_role(
                    role_id
                )['project_roles'][0]
                user_data = panoptes.get_user(
                    role_data['links']['owner']['id']
                )['users'][0]

                return {
                    'id': user_data['id'],
                    'login': user_data['login'],
                    'roles': ', '.join(role_data['roles']),
                }

            collaborators = map(
                get_collaborator, proj_data['links']['project_roles']
            )

            for collaborator in collaborators:
                click.echo('\t%(login)s (%(id)s): %(roles)s' % collaborator)

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
