from accounts.test.accounts_factories import UserFactory
from django.contrib.auth.models import Group
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.test import TestCase

from Collablogation.accounts.perm_constants import view_permission
from .articles_factories import ArticleFactory
from ..services import article_update, article_create, article_delete, create_perms_and_groups_for_article


class CreatePermsAndGroupsForArticleTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.test_article1 = ArticleFactory()
        cls.test_article2 = ArticleFactory()
        cls.test_author1 = cls.test_article1.author
        cls.test_author2 = cls.test_article2.author

    def test_create_perms_and_groups_for_article(self):
        codename, _ = view_permission
        self.assertEqual(Group.objects.all().count(), 0)
        create_perms_and_groups_for_article(instance=self.test_article1.id)
        view_perm = self.test_article1.id + codename
        self.assertEqual(Group.objects.all().count(), 1)
        self.assertEqual(self.test_author1.has_article_perm(view_perm), True)
        self.assertEqual(self.test_author2.has_article_perm(view_perm), False)
        suffixes = ['_can_view_permission',
                    '_can_edit_permission',
                    '_can_hook_inline_comments_permission',
                    '_can_delete_permission']
        perm_names = [f'{id1}{suffix}' for suffix in suffixes]
        for permission_name in perm_names:
            self.assertEqual(self.test_author1.has_perm(permission_name), 1)
            self.assertEqual(self.test_author2.has_perm(permission_name), 0)


class ArticleCreateTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_author1 = UserFactory

    def test_draft_even_if_passed_otherwise(self):
        article = article_create(user=self.test_author1, status=Article.PUBLISHED,
                                 contents='blah blah blah', title='Random title1')
        self.assertEqual(article.status, article.DRAFT)

    def test_article_created_properly(self):
        self.assertEqual(Article.objects.count(), 1)
        article = article_create(user=self.test_author1,
                                 contents='Larum Pepsum ium nosum', title='Random title2')
        self.assertEqual(Article.objects.count(), 2)


class ArticleDeleteTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_article1 = ArticleFactory(title='Random title 1')
        cls.test_article2 = ArticleFactory(title='Random title 2')
        cls.test_author1 = self.test_article1.author
        cls.test_author2 = self.test_article2.author

    def test_article_deleted(self):
        self.assertEqual(get_object_or_404(Article, title='Random title 1'), self.test_article1)
        article_delete(user=self.test_author1, article=self.test_article1)
        self.assertRaises(get_object_or_404(Article, title='Random title 1'), Http404)

    def test_perms_groups_deleted(self):
        pass


class ArticleUpdateTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_article1 = ArticleFactory(title='Random title 1')
        cls.test_article2 = ArticleFactory(title='Random title 2', frozen=True)
        cls.test_author1 = self.test_article1.author
        cls.test_author2 = self.test_article2.author

    def test_frozen_article_can_no_longer_be_updated(self):
        self.assertRaises(PermissionError, article_update(article=self.test_article2,
                                                          data={'title': 'Changed random title'}))

    def test_article_status_published(self):
        pass

    def test_article_status_archived(self):
        pass
