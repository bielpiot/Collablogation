from accounts.tests.accouns_factories import UserFactory
from rest_framework.test import APITestCase

from .articles_factories import ArticleFactory


class ArticleListAPITest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_article1 = ArticleFactory()
        cls.test_author1 = UserFactory()


class ArticleDetailAPITest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_article1 = ArticleFactory()
        cls.test_author1 = UserFactory()


class ArticleCreateAPITest(APITestCase):
    pass


class ArticleUpdateAPITest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_article1 = ArticleFactory()
        cls.test_author1 = UserFactory()


class ArticleDeleteAPITest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_article1 = ArticleFactory()
        cls.test_author1 = UserFactory()
