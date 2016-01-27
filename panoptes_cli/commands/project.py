import click

from panoptes_cli.scripts.panoptes import cli

@cli.command()
@click.option('--id', help='Project ID', required=False, type=int)
@click.option('--display-name')
@click.option('--sets', is_flag=True)
@click.option('--roles', is_flag=True)
@click.option('--verbose', '-v', is_flag=True)
@click.argument('slug', required=False)
@click.pass_context
def project(ctx, id, display_name, slug, sets, roles, verbose):
    projects = ctx.parent.panoptes.get_projects(
        id, slug=slug, display_name=display_name
    )

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
                lambda id: ctx.parent.panoptes.get_subject_set(
                    id
                )['subject_sets'][0],
                proj_data['links']['subject_sets']
            )

            for subject_set in subject_sets:
                click.echo('\t%(id)s: %(display_name)s' % subject_set)

            click.echo('')

        if roles or verbose:
            click.echo('Roles:')

            def get_collaborator(role_id):
                role_data = ctx.parent.panoptes.get_project_role(
                    role_id
                )['project_roles'][0]
                user_data = ctx.parent.panoptes.get_user(
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

