import responses

from microblog_to_sqlite.client import MicroBlogClient

from . import fixtures


@responses.activate
def test_micro_blog_client__request():
    token = "IAmAMicroBlogApplicationToken"
    url = "https://micro.blog/posts/myles"

    responses.add(
        responses.Response(
            method="GET",
            url=url,
            json=fixtures.FEED_MICROBLOG,
        ),
    )

    client = MicroBlogClient(token=token)
    client.request(method="GET", url=url)

    assert len(responses.calls) == 1
    call = responses.calls[-1]

    assert call.request.url == url

    assert "Authorization" in call.request.headers
    assert call.request.headers["Authorization"] == f"Bearer {token}"

    assert "User-Agent" in call.request.headers
    assert (
        call.request.headers["User-Agent"]
        == "microblog-to-sqlite (+https://github.com/myles/microblog-to-sqlite)"
    )
