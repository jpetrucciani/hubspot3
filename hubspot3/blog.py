"""
hubspot blog api client
"""
import json
from hubspot3.base import BaseClient

BLOG_API_VERSION = "1"


class BlogClient(BaseClient):
    """
    provides a client for accessing hubspot blog info
    """

    def _get_path(self, subpath):
        return "blog/v{}/{}".format(BLOG_API_VERSION, subpath)

    def get_blogs(self, **options):
        return self._call("list.json", **options)

    def get_blog_info(self, blog_guid, **options):
        return self._call(blog_guid, **options)

    def get_posts(self, blog_guid, **options):
        return self._call("{}/posts.json".format(blog_guid), **options)

    def get_draft_posts(self, blog_guid, **options):
        return self._call(
            "{}/posts.json".format(blog_guid), params={"draft": "true"}, **options
        )

    def get_published_posts(self, blog_guid, **options):
        params = dict(draft="false")
        params.update(options)
        return self._call("{}/posts.json".format(blog_guid), params=params)

    # Spelled wrong but left for compat
    def get_pulished_posts(self, blog_guid, **options):
        return self._call(
            "{}/posts.json".format(blog_guid), params={"draft": "false"}, **options
        )

    def get_blog_comments(self, blog_guid, **options):
        return self._call("{}/comments.json".format(blog_guid), **options)

    def get_post(self, post_guid, **options):
        return self._call("posts/{}.json".format(post_guid), **options)

    def get_post_comments(self, post_guid, **options):
        return self._call("posts/{}/comments.json".format(post_guid), **options)

    def get_comment(self, comment_guid, **options):
        return self._call("comments/{}.json".format(comment_guid), **options)

    def create_post(
        self,
        blog_guid,
        author_name,
        author_email,
        title,
        summary,
        content,
        tags,
        meta_desc,
        meta_keyword,
        **options
    ):
        post = json.dumps(
            dict(
                title=title,
                authorDisplayName=author_name,
                authorEmail=author_email,
                summary=summary,
                body=content,
                tags=tags,
                metaDescription=meta_desc,
                metaKeywords=meta_keyword,
            )
        )
        raw_response = self._call(
            "{}/posts.json".format(blog_guid),
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
        meta_keyword=None,
        tags=None,
        **options
    ):
        tags = tags or []
        update_param_translation = dict(
            itle="title",
            summary="summary",
            content="body",
            meta_desc="metaDescription",
            meta_keyword="metaKeywords",
            tags="tags",
        )
        post_dict = dict(
            [
                (k, locals()[p])
                for p, k in update_param_translation.items()
                if locals().get(p)
            ]
        )
        post = json.dumps(post_dict)
        raw_response = self._call(
            "posts/{}.json".format(post_guid),
            data=post,
            method="PUT",
            content_type="application/json",
            raw_output=True,
            **options
        )
        return raw_response

    def publish_post(
        self, post_guid, should_notify, publish_time=None, is_draft="false", **options
    ):
        post = json.dumps(
            dict(
                published=publish_time, draft=is_draft, sendNotifications=should_notify
            )
        )
        raw_response = self._call(
            "posts/{}.json".format(post_guid),
            data=post,
            method="PUT",
            content_type="application/json",
            raw_output=True,
            **options
        )
        return raw_response

    def create_comment(
        self, post_guid, author_name, author_email, author_uri, content, **options
    ):
        post = json.dumps(
            dict(
                anonyName=author_name,
                anonyEmail=author_email,
                anonyUrl=author_uri,
                comment=content,
            )
        )
        raw_response = self._call(
            "posts/{}/comments.json".format(post_guid),
            data=post,
            method="POST",
            content_type="application/json",
            raw_output=True,
            **options
        )
        return raw_response
