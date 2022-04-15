from django.test import TestCase
from django.core.exceptions import FieldError
from ..models import Article

from .articles_factories import ArticleFactory


class TestPost(TestCase):

    def test_unique_slug_creation(self):
        error_msg = 'Please provide different title'
        with self.assertRaisesMessage(FieldError, error_msg):
            ArticleFactory.create_batch(11, title='trying to create some article')
        q = Article.objects.all()
        self.assertEqual(len(q), 10)
