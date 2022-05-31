import yaml

import click

from panoptes_cli.scripts.panoptes import cli
from panoptes_client import Workflow


@cli.group()
def workflow():
    """Contains commands for managing workflows."""
    pass


@workflow.command()
@click.argument('workflow-id', required=False, type=int)
@click.option(
    '--project-id',
    '-p',
    help="List workflows linked to the given project.",
    required=False,
    type=int,
)
@click.option(
    '--quiet',
    '-q',
    is_flag=True,
    help='Only print workflow IDs (omit names).',
)
def ls(workflow_id, project_id, quiet):
    """Lists workflow IDs and names."""

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


@workflow.command()
@click.argument('workflow-id', required=True)
def info(workflow_id):
    workflow = Workflow.find(workflow_id)
    click.echo(yaml.dump(workflow.raw))


@workflow.command(name='retire-subjects')
@click.argument('workflow-id', type=int)
@click.argument('subject-ids', type=int, nargs=-1)
@click.option(
    '--reason',
    '-r',
    help="The reason for retiring the subject.",
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
    """
    Retires subjects from the given workflow.

    The subjects will no longer be served to volunteers for classification.
    """

    workflow = Workflow.find(workflow_id)
    workflow.retire_subjects(subject_ids, reason)


@workflow.command(name='unretire-subjects')
@click.argument('workflow-id', type=int)
@click.argument('subject-ids', type=int, nargs=-1, required=True)
def unretire_subjects(workflow_id, subject_ids):
    """
    Unretires subjects for the given workflow.

    The subjects will be cleared of retirement data and be available for volunteers to classify.
    """

    workflow = Workflow.find(workflow_id)
    workflow.unretire_subjects(subject_ids)


@workflow.command(name='unretire-subject-sets')
@click.argument('workflow-id', type=int)
@click.argument('subject-set-ids', type=int, nargs=-1, required=True)
def unretire_subject_sets(workflow_id, subject_set_ids):
    """
    Unretires all the subjects in the subject sets for the given workflow.

    All subjects linked to the supplied subject sets will be cleared of retirement data and be available for volunteers to classify.
    """

    workflow = Workflow.find(workflow_id)
    workflow.unretire_subjects_by_subject_set(subject_set_ids)


@workflow.command(name='add-subject-sets')
@click.argument('workflow-id', type=int)
@click.argument('subject-set-ids', type=int, nargs=-1)
def add_subject_sets(workflow_id, subject_set_ids):
    """Links existing subject sets to the given workflow."""

    workflow = Workflow.find(workflow_id)
    workflow.add_subject_sets(subject_set_ids)



@workflow.command(name='remove-subject-sets')
@click.argument('workflow-id', type=int)
@click.argument('subject-set-ids', type=int, nargs=-1)
def remove_subject_sets(workflow_id, subject_set_ids):
    """Unlinks the given subject sets from the given workflow."""

    workflow = Workflow.find(workflow_id)
    workflow.remove_subject_sets(subject_set_ids)


@workflow.command()
@click.argument('workflow-id', type=int)
def activate(workflow_id):
    """Activates the given workflow."""

    workflow = Workflow.find(workflow_id)
    workflow.active = True
    workflow.save()


@workflow.command()
@click.argument('workflow-id', type=int)
def deactivate(workflow_id):
    """Deactivates the given workflow."""

    workflow = Workflow.find(workflow_id)
    workflow.active = False
    workflow.save()


@workflow.command(name="download-classifications")
@click.argument('workflow-id', required=True, type=int)
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
def download_classifications(
    workflow_id,
    output_file,
    generate,
    generate_timeout
):
    """
    Downloads a workflow-specific classifications export for the given workflow.

    OUTPUT_FILE will be overwritten if it already exists. Set OUTPUT_FILE to -
    to output to stdout.
    """

    workflow = Workflow.find(workflow_id)

    if generate:
        click.echo("Generating new export...", err=True)

    export = workflow.get_export(
        'classifications',
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


@workflow.command()
@click.option(
    '--force',
    '-f',
    is_flag=True,
    help='Delete without asking for confirmation.',
)
@click.argument('workflow-ids', required=True, nargs=-1, type=int)
def delete(force, workflow_ids):
    for workflow_id in workflow_ids:
        workflow = Workflow.find(workflow_id)
        if not force:
            click.confirm(
                'Delete workflow {} ({})?'.format(
                    workflow_id,
                    workflow.display_name,
                ),
                abort=True,
            )
        workflow.delete()


def echo_workflow(workflow):
    click.echo(
        u'{} {}'.format(
            workflow.id,
            workflow.display_name
        )
    )
