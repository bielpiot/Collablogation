from django.test import TestCase
from django.contrib.auth.models import Permission, Group
from .comment_factories import CommentFactory
from ..models import Comment, InlineComment
from ...articles.tests.articles_factories import ArticleFactory
from Collablogation.accounts.tests.accounts_factories import UserFactory
from ..services import comment_create
from ...articles.services import create_perms_and_groups_for_article


class CommentCreateTest(TestCase):
    def setUp(self) -> None:
        self.test_article1 = ArticleFactory(title='test article 1')
        self.test_article2 = ArticleFactory(title='test article 2')
        self.test_author1 = self.test_article1.author
        self.test_author2 = self.test_article2.author
        create_perms_and_groups_for_article(instance=self.test_article1.id)
        create_perms_and_groups_for_article(instance=self.test_article2.id)

    def test_permission_denial(self):
        pass

    def test_parent_constraint(self):
        pass

    def test_comment_creation(self):
        pass


class InlineCommentHookTest(TestCase):
    pass
