from accounts.perm_constants import FULL_ACCESS_SUFFIX
from articles.models import Article
from articles.services import create_perms_and_groups_for_article
from articles.tests.articles_factories import ArticleFactory
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError, PermissionDenied
from django.test import TestCase

from .comment_factories import CommentFactory
from ..models import Comment
from ..services import comment_create, comment_update, comment_delete


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

    # def test_permission_to_add_comment_to_restricted_article_denial(self):
    #     with self.assertRaises(PermissionDenied):
    #         comment_create(user=self.test_author2,
    #                        article=self.test_article1,
    #                        contents='lorum ipsum')

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


class CommentUpdateTest(TestCase):
    def setUp(self):
        self.test_article1 = ArticleFactory(status=Article.PUBLISHED)
        self.test_article2 = ArticleFactory()
        self.test_comment1 = CommentFactory(article=self.test_article1)
        self.test_comment2 = CommentFactory(parent_comment=self.test_comment1, article=self.test_article1)
        self.test_author1 = self.test_comment1.author
        self.test_author2 = self.test_comment2.author
        self.test_data = {'contents': 'Blablabla'}

    def test_comment_update_rejected_if_not_author(self):
        with self.assertRaises(PermissionDenied):
            comment_update(user=self.test_author1, comment=self.test_comment2,
                           data=self.test_data, article=self.test_article1)

    def test_comment_update_rejected_if_answered(self):
        with self.assertRaises(PermissionDenied):
            comment_update(user=self.test_author1, comment=self.test_comment1,
                           data=self.test_data, article=self.test_article1)

    def test_comment_update(self):
        comment_update(user=self.test_author2, comment=self.test_comment2,
                       data=self.test_data, article=self.test_article1)
        self.assertEqual(self.test_comment2.contents, 'Blablabla')


class CommentDeleteTest(TestCase):
    def setUp(self):
        self.test_article1 = ArticleFactory(status=Article.PUBLISHED)
        self.test_comment1 = CommentFactory(parent_comment=None, article=self.test_article1)
        self.test_comment2 = CommentFactory(parent_comment=self.test_comment1, article=self.test_article1)
        self.test_author1 = self.test_comment1.author
        self.test_author2 = self.test_comment2.author

    def test_comment_delete_denied_if_not_author(self):
        with self.assertRaises(PermissionDenied):
            comment_delete(comment=self.test_comment2, user=self.test_author1, article=self.test_article1)

    def test_getting_frozen_if_answered(self):
        self.assertEqual(self.test_comment1.frozen, False)
        comment_delete(comment=self.test_comment1, user=self.test_author1, article=self.test_article1)
        self.assertEqual(self.test_comment1.frozen, True)
        self.assertEqual(self.test_comment1.contents, 'Comment deleted')

    def test_proper_delete_conduct(self):
        self.assertEqual(Comment.objects.count(), 2)
        comment_delete(comment=self.test_comment2, user=self.test_author2, article=self.test_article1)
        self.assertEqual(Comment.objects.count(), 1)


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
