from accounts.tests.accounts_factories import UserFactory
from articles.tests.articles_factories import ArticleFactory
from django.test import TestCase

from ..models import Comment


class CommentModelsTest(TestCase):
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

    def test_thread_id_assignment(self):
        self.assertEqual(self.comment1.thread_id, self.comment1.id)
        self.assertEqual(self.comment2.thread_id, self.comment1.thread_id)

    def test_uid_creation(self):
        self.assertNotEqual(self.comment1.uid, self.comment2.uid)
        self.assertEqual(len(self.comment1.uid), 22)
