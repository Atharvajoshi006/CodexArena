import json

from django.contrib.auth.models import User
from django.test import TestCase

from .models import BlogComment, BlogPost


class BlogViewTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="builder", password="testpass123")
        self.other = User.objects.create_user(
            username="teammate",
            first_name="Team",
            last_name="Mate",
            password="testpass123",
        )
        self.post = BlogPost.objects.create(
            author=self.author,
            content="Deployed a cleaner search experience today.",
            tag="tips",
        )
        BlogComment.objects.create(
            post=self.post,
            author=self.other,
            content="Nice upgrade. The search feels more reliable.",
        )

    def test_blogs_view_provides_search_and_filter_context(self):
        response = self.client.get("/blogs/?q=search&tag=tips")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["search_query"], "search")
        self.assertEqual(response.context["active_tag"], "tips")
        self.assertEqual(response.context["total_posts"], 1)
        self.assertEqual(response.context["visible_posts_count"], 1)
        self.assertContains(response, "Deployed a cleaner search experience today.")


class BlogCommentApiTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="builder", password="testpass123")
        self.commenter = User.objects.create_user(username="reviewer", password="testpass123")
        self.post = BlogPost.objects.create(
            author=self.author,
            content="We shipped comment persistence today.",
            tag="api",
        )

    def test_comment_create_persists_to_backend(self):
        self.client.login(username="reviewer", password="testpass123")

        response = self.client.post(
            f"/api/blogs/{self.post.id}/comments/create/",
            data=json.dumps({"content": "Looks good from the backend side too."}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(BlogComment.objects.filter(post=self.post).count(), 1)
        comment = BlogComment.objects.get(post=self.post)
        self.assertEqual(comment.author, self.commenter)
        self.assertEqual(comment.content, "Looks good from the backend side too.")

        payload = response.json()
        self.assertEqual(payload["post_id"], self.post.id)
        self.assertEqual(payload["comments_count"], 1)
        self.assertEqual(payload["author"], "reviewer")

    def test_comment_create_rejects_blank_content(self):
        self.client.login(username="reviewer", password="testpass123")

        response = self.client.post(
            f"/api/blogs/{self.post.id}/comments/create/",
            data=json.dumps({"content": "   "}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(BlogComment.objects.count(), 0)


class DeploymentReadinessTests(TestCase):
    def test_health_check_returns_ok(self):
        response = self.client.get("/health/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})
