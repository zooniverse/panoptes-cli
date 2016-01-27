import click

from panoptes_cli.scripts.panoptes import cli

@cli.group()
@click.pass_context
def subject(ctx):
    ctx.panoptes = ctx.parent.panoptes

@subject.command()
@click.argument('subject_id', required=True, type=int)
@click.pass_context
def ls(ctx, subject_id):
    subject = ctx.parent.panoptes.get_subject(subject_id)['subjects'][0]
    project = ctx.parent.panoptes.get_project(subject['links']['project'])

    click.echo('Project: %s' % project['display_name'])

    click.echo('Locations:')

    for location in subject['locations']:
        for mimetype, uri in location.items():
            click.echo('\t%s: %s' % (mimetype, uri))
