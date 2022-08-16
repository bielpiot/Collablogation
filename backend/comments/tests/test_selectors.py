from articles.tests.articles_factories import ArticleFactory
from django.test import TestCase


class CommentsThreadTest(TestCase):
    def setUp(self):
        self.article1 = ArticleFactory()
