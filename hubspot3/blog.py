"""
hubspot blog api client
"""
import json
from hubspot3.base import BaseClient
from typing import Dict


BLOG_API_VERSION = "2"
COMMENTS_API_VERSION = "3"
TOPICS_API_VERSION = "3"


class BlogClient(BaseClient):
    """
    provides a client for accessing hubspot blog info
    """

    def _get_path(self, subpath: str) -> str:
        return "content/api/v{}/{}".format(BLOG_API_VERSION, subpath)

    def get_blogs(self, **options):
        return self._call("blogs", **options)

    def get_blog_info(self, blog_guid, **options):
        return self._call("blogs/{}".format(blog_guid), **options)

    def get_posts(self, blog_guid: str, **options) -> Dict:
        if "params" not in options:
            options["params"] = {}
        options["params"].update({"content_group_id": blog_guid})
        return self._call("blog-posts", **options)

    def get_draft_posts(self, blog_guid: str, **options) -> Dict:
        if "params" not in options:
            options["params"] = {}
        options["params"].update({"content_group_id": blog_guid, "state": "DRAFT"})
        return self._call("blog-posts", **options)

    def get_published_posts(self, blog_guid: str, **options) -> Dict:
        if "params" not in options:
            options["params"] = {}
        options["params"].update({"content_group_id": blog_guid, "state": "PUBLISHED"})
        return self._call("blog-posts", **options)

    # Spelled wrong but left for compat
    def get_pulished_posts(self, blog_guid: str, **options) -> Dict:
        return self.get_published_posts(blog_guid, **options)

    def get_post(self, post_guid: str, **options) -> Dict:
        return self._call("blog-posts/{}".format(post_guid), **options)

    def create_post(
        self, blog_guid, author_id, title, summary, content, meta_desc, **options
    ):
        post = json.dumps(
            dict(
                content_group_id=blog_guid,
                name=title,
                blog_author_id=author_id,
                post_summary=summary,
                post_body=content,
                meta_description=meta_desc,
            )
        )
        raw_response = self._call(
            "blog-posts",
            data=post,
            method="POST",
            content_type="application/json",
            raw_output=True,
            **options
        )
        return raw_response

    def update_post(
        self,
        post_guid,
        title=None,
        summary=None,
        content=None,
        meta_desc=None,
        **options
    ):
        update_param_translation = dict(
            title="name",
            summary="post_summary",
            content="post_body",
            meta_desc="meta_description",
        )
        posts = {
            k: locals()[p]
            for p, k in update_param_translation.items()
            if locals().get(p)
        }

        post = json.dumps(posts)
        raw_response = self._call(
            "blog-posts/{}".format(post_guid),
            data=post,
            method="PUT",
            content_type="application/json",
            raw_output=True,
            **options
        )
        return raw_response

    def publish_post(self, post_guid: str, **options) -> Dict:
        post = json.dumps(dict(action="schedule-publish"))
        raw_response = self._call(
            "blog-posts/{}/publish-action".format(post_guid),
            data=post,
            method="PUT",
            content_type="application/json",
            raw_output=True,
            **options
        )
        return raw_response


class BlogCommentsClient(BaseClient):
    """
    provides a client for accessing hubspot comments info
    """

    def _get_path(self, subpath: str) -> str:
        return "comments/v{}/{}".format(COMMENTS_API_VERSION, subpath)

    def get_comments(self, **options):
        return self._call("comments", **options)

    def get_post_comments(self, post_guid: str, **options) -> Dict:
        if "params" not in options:
            options["params"] = {}
        options["params"].update({"contentId": post_guid})
        return self._call("comments", **options)

    def get_comment(self, comment_guid: str, **options) -> Dict:
        return self._call("comments/{}".format(comment_guid), **options)

    def create_comment(
        self,
        blog_guid,
        post_guid,
        author_name,
        author_email,
        author_uri,
        content,
        **options
    ):
        post = dict(
            collectionId=blog_guid,
            contentId=post_guid,
            userName=author_name,
            userEmail=author_email,
            userUrl=author_uri,
            comment=content,
        )
        raw_response = self._call(
            "comments",
            data=post,
            method="POST",
            content_type="application/json",
            raw_output=True,
            **options
        )
        return raw_response


class BlogTopicsClient(BaseClient):
    """
    provides a client for accessing hubspot blog topics info
    """

    def _get_path(self, subpath: str) -> str:
        return "blogs/v{}/{}".format(TOPICS_API_VERSION, subpath)

    def get_topics(self, **options):
        return self._call("topics", **options)
