from typing import Tuple

from requests import PreparedRequest, Request, Response, Session
from requests.auth import AuthBase


class MicroBlogAuth(AuthBase):
    def __init__(self, token: str):
        self.token = token

    def __call__(self, r):
        r.headers["Authorization"] = f"Bearer {self.token}"
        return r


class MicroBlogClient:
    def __init__(self, token: str):
        self.base_url = "https://micro.blog"

        self.session = Session()
        self.session.auth = MicroBlogAuth(token)

        self.session.headers[
            "User-Agent"
        ] = "microblog-to-sqlite (+https://github.com/myles/microblog-to-sqlite)"

    def request(
        self, method: str, url: str, timeout: Tuple[int, int] = None, **kwargs
    ) -> Tuple[PreparedRequest, Response]:
        request = Request(method=method.upper(), url=url, **kwargs)
        prepped = self.session.prepare_request(request)
        response = self.session.send(prepped, timeout=timeout)

        return prepped, response

    def get_posts(self, username: str) -> Tuple[PreparedRequest, Response]:
        """
        JSON posts written by the given user.
        """
        return self.request("GET", f"{self.base_url}/posts/{username}")

    def get_bookshelves(self) -> Tuple[PreparedRequest, Response]:
        """
        Bookshelves for the current authenticated user.
        """
        return self.request("GET", f"{self.base_url}/books/bookshelves")

    def get_books_in_bookshelf(self, bookshelf_id: int) -> Tuple[PreparedRequest, Response]:
        """
        Books in the bookshelf for the current authenticated user.
        """
        return self.request("GET", f"{self.base_url}/books/bookshelves/{bookshelf_id}")
