from django.test import TestCase
from django.db import IntegrityError
from ..models import Comment, InlineComment
from .comment_factories import CommentFactory
from articles.tests.articles_factories import ArticleFactory
from accounts.tests.accounts_factories import UserFactory
from django.core.exceptions import ValidationError


class HasChildrenPropertyTest(TestCase):
    def setUp(self) -> None:
        self.user1 = UserFactory()
        self.user2 = UserFactory()
        self.article = ArticleFactory()
        self.comment1 = Comment.objects.create(author=self.user1,
                                               article=self.article,
                                               parent_comment=None,
                                               contents='aa')
        self.comment2 = Comment.objects.create(author=self.user2,
                                               article=self.article,
                                               parent_comment=self.comment1,
                                               contents='bb')

    def test_has_children(self):
        self.assertEqual(self.comment1.has_children, 1)
        self.assertEqual(self.comment2.has_children, 0)
