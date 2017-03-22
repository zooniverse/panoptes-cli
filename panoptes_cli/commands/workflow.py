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


@workflow.command()
@click.argument('workflow-id', type=int)
@click.argument('subject-set-ids', type=int, nargs=-1)
def add_subject_sets(workflow_id, subject_set_ids):
    workflow = Workflow.find(workflow_id)
    workflow.add_subject_sets(subject_set_ids)


@workflow.command()
@click.argument('workflow-id', type=int)
@click.argument('subject-set-ids', type=int, nargs=-1)
def remove_subject_sets(workflow_id, subject_set_ids):
    workflow = Workflow.find(workflow_id)
    workflow.remove_subject_sets(subject_set_ids)


@workflow.command()
@click.argument('workflow-id', type=int)
def activate(workflow_id):
    workflow = Workflow.find(workflow_id)
    workflow.active = True
    workflow.save()


@workflow.command()
@click.argument('workflow-id', type=int)
def deactivate(workflow_id):
    workflow = Workflow.find(workflow_id)
    workflow.active = False
    workflow.save()


@workflow.command()
@click.option('--workflow-id', required=True, type=int)
@click.option('--output', required=True, type=click.File('wb'))
@click.option('--generate/--no-generate', required=False)
@click.option('--generate-timeout', required=False, type=int, default=3600)
def download(workflow_id, output, generate, generate_timeout):
    workflow = Workflow.find(workflow_id)
    export = workflow.get_export(
        'classifications',
        generate=generate,
        wait_timeout=generate_timeout
    )
    for chunk in export.iter_content():
        output.write(chunk)


def echo_workflow(workflow):
    click.echo(
        u'{} {}'.format(
            workflow.id,
            workflow.display_name
        )
    )
