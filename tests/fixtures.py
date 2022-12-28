FEED_ITEM_ONE = {
    "_microblog": {
        "date_relative": "2021-01-23  7:30 pm",
        "date_timestamp": 1611448246,
        "is_bookmark": False,
        "is_conversation": True,
        "is_deletable": True,
        "is_favorite": False,
        "is_linkpost": False,
        "is_mention": False,
    },
    "author": {
        "_microblog": {"username": "myles"},
        "avatar": "https://avatars.micro.blog/avatars/2022/1383.jpg",
        "name": "Myles Braithwaite",
        "url": "https://mylesb.ca/",
    },
    "content_html": "<p>Hello, World!</p>",
    "date_published": "2021-01-24T00:30:46+00:00",
    "id": "10906342",
    "url": "https://myles.social/2022/11/21/its-a-bit.html",
}

FEED_MICROBLOG = {
    "about": "https://micro.blog/about/api",
    "id": "1383",
    "username": "myles",
    "bio": "",
    "is_following": True,
    "is_you": True,
    "following_count": 28,
    "discover_count": 0,
}

FEED_AUTHOR = {
    "name": "Myles Braithwaite",
    "url": "https://mylesb.ca/",
    "avatar": "https://avatars.micro.blog/avatars/2022/1383.jpg",
}

FEED = {
    "version": "https://jsonfeed.org/version/1",
    "title": "Micro.blog — Myles Braithwaite",
    "home_page_url": "https://micro.blog/",
    "feed_url": "https://micro.blog/posts/myles",
    "_microblog": FEED_MICROBLOG,
    "author": FEED_AUTHOR,
    "items": [FEED_ITEM_ONE],
}
