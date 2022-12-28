from microblog_to_sqlite import service

from . import fixtures


def test_transform_author():
    author = fixtures.FEED_AUTHOR.copy()
    microblog = fixtures.FEED_MICROBLOG.copy()

    service.transform_author(author=author, microblog=microblog)

    assert author == {
        "id": microblog["id"],
        "username": microblog["username"],
        "name": author["name"],
        "avatar": author["avatar"],
        "url": author["url"],
    }


def test_transform_post():
    post = fixtures.FEED_ITEM_ONE.copy()

    service.transform_post(post)

    assert post == {
        "id": post["id"],
        "content_html": post["content_html"],
        "url": post["url"],
        "date_published": post["date_published"],
    }
