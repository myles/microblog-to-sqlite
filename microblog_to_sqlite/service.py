import json
from pathlib import Path
from typing import Any, Dict, List

from sqlite_utils import Database

from .client import MicroBlogClient


def open_database(db_file_path: Path) -> Database:
    """
    Open the Micro.blog SQLite database.
    """
    return Database(db_file_path)


def build_database(db: Database):
    """
    Build the Micro.blog SQLite database structure.
    """
    table_names = set(db.table_names())

    if "authors" not in table_names:
        db["authors"].create(
            columns={
                "id": int,
                "username": str,
                "name": str,
                "avatar": str,
                "url": str,
            },
            pk="id",
        )
        db["authors"].enable_fts(["username", "name"], create_triggers=True)

    if "posts" not in table_names:
        db["posts"].create(
            columns={
                "id": int,
                "content_text": str,
                "content_html": str,
                "url": str,
                "date_published": str,
                "author_id": str,
            },
            pk="id",
            foreign_keys=(("author_id", "authors", "id"),),
        )

    posts_indexes = {tuple(i.columns) for i in db["posts"].indexes}
    if ("author_id",) not in posts_indexes:
        db["posts"].create_index(["author_id"])


def microblog_client(auth_file_path: str) -> MicroBlogClient:
    """
    Returns a fully authenticated MicroBlogClient.
    """
    with Path(auth_file_path).absolute().open() as file_obj:
        raw_auth = file_obj.read()

    auth = json.loads(raw_auth)

    return MicroBlogClient(token=auth["microblog_token"])


def get_username(auth_file_path: str) -> str:
    """
    Returns the user's Micro.blog username.
    """
    with Path(auth_file_path).absolute().open() as file_obj:
        raw_auth = file_obj.read()

    auth = json.loads(raw_auth)

    return auth["microblog_username"]


def get_posts(username: str, client: MicroBlogClient) -> Dict[str, Any]:
    """
    Get authenticated user's posts.
    """
    _, response = client.posts(username)
    response.raise_for_status()
    return response.json()


def transform_author(author: Dict[str, Any], microblog: Dict[str, Any]):
    """
    Transformer a Micro.blog author, so it can be safely saved to the SQLite
    database.
    """
    to_remove = [k for k in author.keys() if k not in ("name", "avatar", "url")]
    for key in to_remove:
        del author[key]

    author["id"] = microblog["id"]
    author["username"] = microblog["username"]


def transform_post(post: Dict[str, Any]):
    """
    Transformer a Micro.blog post, so it can be safely saved to the SQLite
    database.
    """
    to_remove = [
        k
        for k in post.keys()
        if k
        not in ("id", "content_text", "content_html", "url", "date_published")
    ]
    for key in to_remove:
        del post[key]


def save_posts(db: Database, feed: Dict[str, Any]):
    """
    Save Micro.blog posts to the SQLite database.
    """
    build_database(db)

    author = feed["author"]
    microblog = feed["_microblog"]
    transform_author(author, microblog)
    db["authors"].insert(author, pk="id", alter=True, replace=True)

    posts = feed["items"]
    for post in posts:
        transform_post(post)
        post["author_id"] = microblog["id"]

    db["posts"].insert_all(posts, pk="id", alter=True, replace=True)
