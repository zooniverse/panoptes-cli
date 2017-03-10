import click

from panoptes_cli.scripts.panoptes import cli
from panoptes_client import Workflow


@cli.group()
def workflow():
    pass


@workflow.command()
@click.argument('workflow-id', required=False, type=int)
@click.option('--project-id', required=False, type=int)
def ls(workflow_id, project_id):
    if workflow_id and not project_id:
        echo_workflow(Workflow.find(workflow_id))
    else:
        args = {}
        if project_id:
            args['project_id'] = project_id
        if workflow_id:
            args['workflow_id'] = workflow_id
        map(echo_workflow, Workflow.where(**args))


@workflow.command()
@click.argument('workflow-id', type=int)
@click.argument('subject-ids', type=int, nargs=-1)
@click.option(
    '--reason',
    type=click.Choice((
        'classification_count',
        'flagged',
        'blank',
        'consensus',
        'other'
    )),
    default='other'
)
def retire_subjects(workflow_id, subject_ids, reason):
    workflow = Workflow.find(workflow_id)
    workflow.retire_subjects(subject_ids, reason)


def echo_workflow(workflow):
    click.echo(
        u'{} {}'.format(
            workflow.id,
            workflow.display_name
        )
    )
