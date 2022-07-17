from articles.services import create_perms_and_groups_for_article
from articles.tests.articles_factories import ArticleFactory
from rest_framework.test import APITestCase


class CommentListApi(APITestCase):
    pass


class GetCommentDetailTest(APITestCase):
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

    def test_access_denial_beta_article(self):
        pass

    def test_access_granted_published_article(self):
        pass

    def test_access_granted_user_has_article_perm(self):
        pass


class CreateCommentTest(APITestCase):
    def setUp(self):
        pass

    def test_permission_denied_article_status(self):
        pass

    def test_permission_denied_user_perms(self):
        pass

    def test_comment_created_properly(self):
        pass


class UpdateCommentTest(APITestCase):
    pass


class DeleteCommentTest(APITestCase):
    pass
