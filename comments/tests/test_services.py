from django.test import TestCase
from django.contrib.auth.models import Permission, Group
from django.core.exceptions import PermissionDenied, ValidationError
from .comment_factories import CommentFactory, InlineCommentFactory
from ..models import Comment, InlineComment
from articles.tests.articles_factories import ArticleFactory
from accounts.tests.accounts_factories import UserFactory
from ..services import comment_create
from articles.services import create_perms_and_groups_for_article
from articles.perm_constants import FULL_ACCESS_SUFFIX
from ..services import comment_create


class CommentCreateTest(TestCase):
    def setUp(self):
        self.test_article1 = ArticleFactory(title='test article 1', status='draft')
        self.test_article2 = ArticleFactory(title='test article 2', status='published')
        self.test_author1 = self.test_article1.author
        self.test_author2 = self.test_article2.author
        create_perms_and_groups_for_article(instance=self.test_article1)
        create_perms_and_groups_for_article(instance=self.test_article2)
        super_group1 = Group.objects.get(name=str(self.test_article1.id) + FULL_ACCESS_SUFFIX)
        super_group2 = Group.objects.get(name=str(self.test_article2.id) + FULL_ACCESS_SUFFIX)
        self.test_author1.groups.add(super_group1)
        self.test_author1.groups.add(super_group2)
        self.test_comment1 = CommentFactory(article=self.test_article1, parent_comment=None)

    def test_permission_to_add_comment_to_restricted_article_denial(self):
        with self.assertRaises(PermissionDenied):
            comment_create(user=self.test_author2,
                           article=self.test_article1,
                           contents='lorum ipsum')

    def test_parent_constraint(self):
        with self.assertRaises(ValidationError):
            comment_create(user=self.test_author1,
                           article=self.test_article2,
                           contents='iprum losum',
                           parent_comment=self.test_comment1)

    def test_comment_creation(self):
        comment_create(user=self.test_author1,
                       article=self.test_article2,
                       contents='opus magnum')
        self.assertEqual(Comment.objects.filter(article=self.test_article2).exists(), True)


class InlineCommentCreateTest(TestCase):
    def setUp(self):
        self.test_article1 = ArticleFactory(title='test article 1', status='draft')
        self.test_article2 = ArticleFactory(title='test article 2', status='published')
        self.test_author1 = self.test_article1.author
        self.test_author2 = self.test_article2.author
        create_perms_and_groups_for_article(instance=self.test_article1)
        create_perms_and_groups_for_article(instance=self.test_article2)
        super_group1 = Group.objects.get(name=str(self.test_article1.id) + FULL_ACCESS_SUFFIX)
        super_group2 = Group.objects.get(name=str(self.test_article2.id) + FULL_ACCESS_SUFFIX)
        self.test_author1.groups.add(super_group1)
        self.test_author1.groups.add(super_group2)
