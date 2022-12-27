import json
from pathlib import Path

import click

from . import service


@click.group()
@click.version_option()
def cli():
    """
    Save data from Micro.blog to a SQLite database.
    """


@cli.command()
@click.option(
    "-a",
    "--auth",
    type=click.Path(file_okay=True, dir_okay=False, allow_dash=False),
    default="auth.json",
    help="Path to save tokens to, defaults to auth.json",
)
def auth(auth):
    """
    Save Micro.blog authentication credentials to a JSON file.
    """
    auth_file_path = Path(auth).absolute()

    username = click.prompt("Micro.blog username")
    click.echo("")

    click.echo(
        f"Create a new application here: https://micro.blog/account/apps"
    )
    click.echo(
        "Then navigate to newly created application and paste in the following:"
    )
    click.echo("")

    application_token = click.prompt("Your application token")

    auth_file_content = json.dumps(
        {
            "microblog_token": application_token,
            "microblog_username": username,
        },
        indent=4,
    )

    with auth_file_path.open("w") as file_obj:
        file_obj.write(auth_file_content + "\n")


@cli.command()
@click.argument(
    "db_path",
    type=click.Path(file_okay=True, dir_okay=False, allow_dash=False),
    required=True,
)
@click.option(
    "-a",
    "--auth",
    type=click.Path(
        file_okay=True, dir_okay=False, allow_dash=True, exists=True
    ),
    default="auth.json",
    help="Path to auth.json token file",
)
def posts(db_path, auth):
    """
    Save posts for the authenticated user.
    """
    db = service.open_database(db_path)
    client = service.microblog_client(auth)

    username = service.get_username(auth)

    feed = service.get_posts(username, client)
    service.save_posts(db, feed)
