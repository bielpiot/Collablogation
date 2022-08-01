from accounts.tests.accouns_factories import UserFactory
from rest_framework.test import APITestCase

from .articles_factories import ArticleFactory


class ArticleListAPITest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_author1 = UserFactory()
        cls.test_author2 = UserFactory()
        cls.test_author3 = UserFactory()
        cls.test_article1 = ArticleFactory(status='draft', author=cls.test_author1)
        cls.test_article2 = ArticleFactory(status='draft', author=cls.test_author1)
        cls.test_article3 = ArticleFactory(status='draft', author=cls.test_author2)
        cls.test_article4 = ArticleFactory(status='beta', author=cls.test_author1)
        cls.test_article5 = ArticleFactory(status='beta', author=cls.test_author3)
        cls.test_article6 = ArticleFactory(status='beta', author=cls.test_author3)
        cls.test_article7 = ArticleFactory(status='published')
        cls.test_article8 = ArticleFactory(status='archived')
        cls.test_article9 = ArticleFactory(status='archived', author=cls.test_author2)
        cls.test_article10 = ArticleFactory(status='archived', author=cls.test_author2)

    def test_drafts_lists(self):
        pass

    def test_beta_lists(self):
        pass

    def test_published_lists(self):
        pass

    def test_archived_lists(self):
        pass


class ArticleDetailAPITest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_author1 = UserFactory()
        cls.test_author2 = UserFactory()
        cls.test_article1 = ArticleFactory(status='draft', author=cls.test_author1)
        cls.test_article2 = ArticleFactory(status='published', author=cls.test_author1)
        cls.test_article3 = ArticleFactory(status='beta', author=cls.test_author1)
        cls.test_article4 = ArticleFactory(status='archived', author=cls.test_author1)

    def test_access_denied_draft_no_perm(self):
        pass

    def test_access_granted_draft_author(self):
        pass

    def test_access_granted_beta_with_perms(self):
        pass

    def test_access_denied_beta_no_perms(self):
        pass

    def test_access_archived_author(self):
        pass

    def test_access_denied_archived_other_author(self):
        pass


class ArticleCreateAPITest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_author1 = UserFactory()


class ArticleUpdateAPITest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_article1 = ArticleFactory(status='draft')
        cls.test_article2 = ArticleFactory(status='published')
        cls.test_article3 = ArticleFactory(status='beta')
        cls.test_article4 = ArticleFactory(status='archived')
        cls.test_author1 = cls.test_article1.author


class ArticleDeleteAPITest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_article1 = ArticleFactory(status='draft')
        cls.test_article2 = ArticleFactory(status='published')
        cls.test_article3 = ArticleFactory(status='beta')
        cls.test_article4 = ArticleFactory(status='archived')
        cls.test_author1 = cls.test_article1.author
