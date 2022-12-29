import datetime
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
        db["posts"].enable_fts(
            ["content_text", "content_html"], create_triggers=True
        )

    posts_indexes = {tuple(i.columns) for i in db["posts"].indexes}
    if ("author_id",) not in posts_indexes:
        db["posts"].create_index(["author_id"])

    if "bookshelves" not in table_names:
        db["bookshelves"].create(
            columns={
                "id": int,
                "title": str,
            },
            pk="id",
        )
        db["bookshelves"].enable_fts(["title"], create_triggers=True)

    if "books" not in table_names:
        db["books"].create(
            columns={
                "id": int,
                "title": str,
                "authors": str,
                "isbn": str,
            },
            pk="id",
        )
        db["books"].enable_fts(["title", "authors"], create_triggers=True)

    books_indexes = {tuple(i.columns) for i in db["books"].indexes}
    if ("isbn",) not in books_indexes:
        db["books"].create_index(["isbn"])

    if "bookshelves_books" not in table_names:
        db["bookshelves_books"].create(
            columns={
                "bookshelf_id": int,
                "book_id": int,
                "first_seen": str,
            },
            pk=("bookshelf_id", "book_id"),
            foreign_keys=(
                ("bookshelf_id", "bookshelves", "id"),
                ("book_id", "books", "id"),
            ),
        )

    bookshelves_books_indexes = {
        tuple(i.columns) for i in db["bookshelves_books"].indexes
    }
    if ("bookshelf_id",) not in bookshelves_books_indexes:
        db["bookshelves_books"].create_index(["bookshelf_id"])
    if ("book_id",) not in bookshelves_books_indexes:
        db["bookshelves_books"].create_index(["book_id"])


def get_client(auth_file_path: str) -> MicroBlogClient:
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
    Get given user's posts.
    """
    _, response = client.get_posts(username)
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


def get_bookshelves(client: MicroBlogClient) -> Dict[str, Any]:
    """
    Get authenticated user's bookshelves.
    """
    _, response = client.get_bookshelves()
    response.raise_for_status()
    return response.json()


def transformer_bookshelf(bookshelf: Dict[str, Any]):
    """
    Transformer a Micro.blog bookshelf, so it can be safely saved to the SQLite
    database.
    """
    to_remove = [k for k in bookshelf.keys() if k not in ("id", "title")]
    for key in to_remove:
        del bookshelf[key]


def save_bookshelves(db: Database, feed: Dict[str, Any]):
    """
    Save Micro.blog bookshelves to the SQLite database.
    """
    build_database(db)

    bookshelves = feed["items"]
    for bookshelf in bookshelves:
        transformer_bookshelf(bookshelf)

    db["bookshelves"].insert_all(bookshelves, pk="id", alter=True, replace=True)


def get_saved_bookshelf_ids(db: Database) -> List[int]:
    """
    Get a list of the saved Bookshelf IDs.
    """
    return [row["id"] for row in db["bookshelves"].rows]


def get_books_in_bookshelf(
    bookshelf_id: int,
    client: MicroBlogClient,
) -> Dict[str, Any]:
    """
    Get authenticated user's bookshelves.
    """
    _, response = client.get_books_in_bookshelf(bookshelf_id)
    response.raise_for_status()
    return response.json()


def transformer_book(book: Dict[str, Any]):
    """
    Transformer a Micro.blog book, so it can be safely saved to the SQLite
    database.
    """
    authors = book.get("authors", [])
    isbn = book.get("_microblog", {}).get("isbn", "")

    to_remove = [k for k in book.keys() if k not in ("id", "title")]
    for key in to_remove:
        del book[key]

    book["authors"] = ", ".join([a["name"] for a in authors])
    book["isbn"] = isbn


def save_books(
    db: Database,
    feed: Dict[str, Any],
    bookshelf_id: int,
):
    """
    Save Micro.blog books to the SQLite database.
    """
    build_database(db)

    books = feed["items"]
    for book in books:
        transformer_book(book)

    db["books"].insert_all(books, pk="id", alter=True, replace=True)

    first_seen = datetime.datetime.utcnow().isoformat()
    db["bookshelves_books"].insert_all(
        (
            {
                "bookshelf_id": bookshelf_id,
                "book_id": book["id"],
                "first_seen": first_seen,
            }
            for book in books
        ),
        ignore=True,
    )
