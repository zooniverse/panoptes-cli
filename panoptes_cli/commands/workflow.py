import click

from panoptes_cli.scripts.panoptes import cli
from panoptes_client import Workflow

@cli.group()
def workflow():
    pass

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
