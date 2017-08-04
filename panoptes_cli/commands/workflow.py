import click

from panoptes_cli.scripts.panoptes import cli
from panoptes_client import Workflow


@cli.group()
def workflow():
    pass


@workflow.command()
@click.argument('workflow-id', required=False, type=int)
@click.option('--project-id', '-p', required=False, type=int)
@click.option(
    '--quiet',
    '-q',
    is_flag=True,
    help='Only print workflow IDs',
)
def ls(workflow_id, project_id, quiet):
    if workflow_id and not project_id:
        workflow = Workflow.find(workflow_id)
        if quiet:
            click.echo(workflow.id)
        else:
            echo_workflow(workflow)
        return

    args = {}
    if project_id:
        args['project_id'] = project_id
    if workflow_id:
        args['workflow_id'] = workflow_id

    workflows = Workflow.where(**args)
    if quiet:
        click.echo(" ".join([w.id for w in workflows]))
    else:
        for workflow in workflows:
            echo_workflow(workflow)


@workflow.command(name='retire-subjects')
@click.argument('workflow-id', type=int)
@click.argument('subject-ids', type=int, nargs=-1)
@click.option(
    '--reason',
    '-r',
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


@workflow.command(name='add-subject-sets')
@click.argument('workflow-id', type=int)
@click.argument('subject-set-ids', type=int, nargs=-1)
def add_subject_sets(workflow_id, subject_set_ids):
    workflow = Workflow.find(workflow_id)
    workflow.add_subject_sets(subject_set_ids)


@workflow.command(name='remove-subject-sets')
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
@click.argument('workflow-id', required=True, type=int)
@click.argument('output-file', required=True, type=click.File('wb'))
@click.option('--generate', '-g', is_flag=True)
@click.option(
    '--generate-timeout',
    '-T',
    required=False,
    type=int,
)
def download(workflow_id, output_file, generate, generate_timeout):
    workflow = Workflow.find(workflow_id)
    export = workflow.get_export(
        'classifications',
        generate=generate,
        wait_timeout=generate_timeout
    )
    for chunk in export.iter_content():
        output_file.write(chunk)


def echo_workflow(workflow):
    click.echo(
        u'{} {}'.format(
            workflow.id,
            workflow.display_name
        )
    )
