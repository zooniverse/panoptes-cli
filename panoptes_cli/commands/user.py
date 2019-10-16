import yaml

import click

from panoptes_cli.scripts.panoptes import cli
from panoptes_client import Panoptes, User


@cli.group()
def user():
    """Contains commands for retrieving information about users."""

    pass


@user.command()
@click.option(
    '--email',
    '-e',
    help='Search for users by email address (only works if you\'re an admin).',
    type=str,
)
@click.option(
    '--login',
    '-l',
    help='Search for users by login name.',
    type=str,
)
@click.argument('user-id', required=False, type=int)
def info(user_id, email, login):
    """
    Displays information about a user. Defaults to the current user if no ID or
    search criteria are given.
    """

    if (user_id and email) or (user_id and login) or (email and login):
        click.echo(
            'Error: At most only one of user ID, login, or email may be '
            'specified.',
            err=True,
        )
        return -1
    if user_id:
        user = User.find(user_id)
    elif email:
        try:
            user = next(User.where(email=email))
        except StopIteration:
            user = None
        if getattr(user, 'email', '') != email:
            click.echo('User not found', err=True)
            return -1
    else:
        if not login:
            login = Panoptes.client().username
        try:
            user = next(User.where(login=login))
        except StopIteration:
            user = None
        if getattr(user, 'login', '') != login:
            click.echo('User not found', err=True)
            return -1
    click.echo(yaml.dump(user.raw))


@user.command()
@click.option(
    '--force',
    '-f',
    is_flag=True,
    help='Delete without asking for confirmation.',
)
@click.argument('user-ids', required=True, nargs=-1, type=int)
def delete(force, user_ids):
    """
    Deletes a user. Only works if you're an admin.
    """

    for user_id in user_ids:
        user = User.find(user_id)
        if not force:
            click.confirm('Delete user {} ({})?'.format(
                user_id,
                user.login,
            ), abort=True)
        user.delete()


@user.command()
def token():
    """
    Returns the current oauth token and its expiration date.
    """

    click.echo("Token: {}".format(Panoptes.client().get_bearer_token()))
    click.echo("Expiry time: {}".format(Panoptes.client().bearer_expires))