from django.test import TestCase
from django.db import IntegrityError
from ..models import Comment, InlineComment
from .comment_factories import CommentFactory
from Collablogation.articles.tests.articles_factories import ArticleFactory
from Collablogation.accounts.tests.accounts_factories import UserFactory
from django.core.exceptions import ValidationError


class ParentCommentTest(TestCase):
    def setUp(self) -> None:
        self.test_article1 = ArticleFactory(title='test article 1')
        self.test_article2 = ArticleFactory(title='test article 2')
        self.test_comment1 = CommentFactory(article=self.test_article1)
        self.test_author = UserFactory()

    def test_parent_constraint(self):
        # proper comment creation
        Comment.objects.create(article=self.test_article1, parent_comment=self.test_comment1,
                               author=self.test_author, contents='created, no problem')
        q = Comment.objects.all()
        self.assertEqual(len(q), 2)
        # make sure comment pointing to different article than parent comment doesn't get created
        with self.assertRaises(ValidationError):
            Comment.objects.create(article=self.test_article2, parent_comment=self.test_comment1,
                                   author=self.test_author, contents='no pass!')
        self.assertEqual(len(q), 2)


class HasChildrenPropertyTest(TestCase):
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
        self.assertEqual(comment1.has_children, 1)
        self.assertEqual(comment2.has_children, 2)
