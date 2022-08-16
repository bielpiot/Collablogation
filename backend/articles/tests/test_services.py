from accounts.perm_constants import view_permission
from accounts.tests.accounts_factories import UserFactory
from articles.models import Article
from django.contrib.auth.models import Group
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.test import TestCase

from .articles_factories import ArticleFactory
from ..services import (article_create, article_delete, article_update,
                        create_perms_and_groups_for_article)


class CreatePermsAndGroupsForArticleTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.test_article1 = ArticleFactory()
        cls.test_article2 = ArticleFactory()
        cls.test_author1 = cls.test_article1.author
        cls.test_author2 = cls.test_article2.author

    def test_create_perms_and_groups_for_article(self):
        codename, _ = view_permission
        self.assertEqual(Group.objects.count(), 0)
        create_perms_and_groups_for_article(instance=self.test_article1)
        self.assertEqual(Group.objects.count(), 2)
        suffixes = ['_can_view_permission',
                    '_can_edit_permission',
                    '_can_add_inline_comments_permission',
                    '_can_delete_permission']
        perm_names = [f'{self.test_article1.id}{suffix}' for suffix in suffixes]
        for permission_name in perm_names:
            self.assertEqual(self.test_author1.has_article_perm(permission_name), 1)
            self.assertEqual(self.test_author2.has_article_perm(permission_name), 0)

        super_group = Group.objects.get(name=f'{self.test_article1.id}_full_access')
        self.assertEqual(super_group.user_set.count(), 1)
        self.assertIn(self.test_author1, super_group.user_set.all())
        self.assertNotIn(self.test_author2, super_group.user_set.all())


class ArticleCreateTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_author1 = UserFactory()

    def test_draft_even_if_passed_otherwise(self):
        self.assertEqual(Article.objects.count(), 0)
        article = article_create(user=self.test_author1, status=Article.PUBLISHED,
                                 contents='blah blah blah', title='Random title1')
        self.assertEqual(article.status, article.DRAFT)
        self.assertEqual(Article.objects.count(), 1)

    def test_article_created_properly(self):
        self.assertEqual(Article.objects.count(), 0)
        article_create(user=self.test_author1,
                       contents='Larum Pepsum ium nosum', title='Random title2')
        self.assertEqual(Article.objects.count(), 1)


class ArticleDeleteTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_article1 = ArticleFactory(status='draft')
        cls.test_article2 = ArticleFactory(status='published')
        cls.test_author1 = cls.test_article1.author
        cls.test_author2 = cls.test_article2.author

    def test_article_deleted(self):
        article_id = self.test_article1.id
        self.assertEqual(get_object_or_404(Article, id=article_id), self.test_article1)
        article_delete(user=self.test_author1, article=self.test_article1)
        with self.assertRaises(Http404):
            get_object_or_404(Article, id=article_id)

    def test_perms_groups_deleted(self):
        pass


class ArticleUpdateTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_article1 = ArticleFactory(status=Article.DRAFT)
        cls.test_article2 = ArticleFactory(title=Article.BETA)
        cls.test_author1 = cls.test_article1.author
        cls.test_author2 = cls.test_article2.author

    def test_article_status_draft_to_published(self):
        article = self.test_article1
        data = {'status': 'published', 'contents': 'now published'}
        article_update(data=data, article=article)
        self.assertEqual(article.status, Article.PUBLISHED)
        self.assertEqual(article.contents, 'now published')

    def test_article_beta_no_status_change(self):
        article = self.test_article2
        data = {'contents': 'changed beta contents'}
        article_update(data=data, article=article)
        self.assertEqual(article.contents, 'changed beta contents')
