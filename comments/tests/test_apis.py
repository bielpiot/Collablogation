from articles.perm_constants import FULL_ACCESS_SUFFIX
from articles.services import create_perms_and_groups_for_article
from articles.tests.articles_factories import ArticleFactory
from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework.status import HTTP_200_OK, HTTP_403_FORBIDDEN, HTTP_201_CREATED
from rest_framework.test import APITestCase, force_authenticate, APIRequestFactory

from .comment_factories import CommentFactory
from ..apis import CommentDetailAPI, CommentListAPI, CommentDeleteAPI


class CommentListAPITest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_article1 = ArticleFactory(title='test article 1', status='draft')
        cls.test_article2 = ArticleFactory(title='test article 2', status='draft')
        cls.test_article3 = ArticleFactory(title='test article 3', status='beta')
        cls.test_article4 = ArticleFactory(title='test article 4', status='beta')
        cls.test_article3 = ArticleFactory(title='test article 5', status='published')
        cls.test_article4 = ArticleFactory(title='test article 6', status='published')
        cls.test_author1 = cls.test_article1.author
        cls.test_author2 = cls.test_article4.author
        cls.factory = APIRequestFactory()
        cls.view = CommentListAPI.as_view()

    def test_empty_list_for_no_draft_author(self):
        url = reverse('drafts')
        request = self.factory.get(url)
        force_authenticate(request, user=self.test_author2)
        response = self.view(request)

    def test_author_get_list_of_his_drafts(self):
        url = reverse('drafts')
        request = self.factory.get(url)
        force_authenticate(request, user=self.test_author2)
        response = self.view(request)

    def test_published_and_beta_list_free_access(self):
        url = reverse('beta')
        request = self.factory.get(url)
        force_authenticate(request, user=self.test_author2)
        response = self.view(request)


class CommentDetailAPITest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_article1 = ArticleFactory(title='test article 1', status='beta', slug='test-article-1')
        cls.test_article2 = ArticleFactory(title='test article 2', status='published', slug='test-article-2')
        cls.test_author1 = cls.test_article1.author
        cls.test_author2 = cls.test_article2.author
        create_perms_and_groups_for_article(instance=cls.test_article1)
        create_perms_and_groups_for_article(instance=cls.test_article2)
        super_group1 = Group.objects.get(name=str(cls.test_article1.id) + FULL_ACCESS_SUFFIX)
        super_group2 = Group.objects.get(name=str(cls.test_article2.id) + FULL_ACCESS_SUFFIX)
        cls.test_author1.groups.add(super_group1)
        cls.test_author1.groups.add(super_group2)
        cls.test_comment1 = CommentFactory(article=cls.test_article1)
        cls.test_comment2 = CommentFactory(article=cls.test_article2)
        cls.factory = APIRequestFactory()
        cls.view = CommentDetailAPI.as_view()

    def test_access_denial_beta_article(self):
        comment_uid = self.test_comment1.uid
        article_slug = self.test_article1.slug
        kwargs = {"comment_uid": comment_uid, "article_slug": article_slug}
        url = reverse('beta:comments:detail', kwargs=kwargs)
        request = self.factory.get(url)
        force_authenticate(request, user=self.test_author2)
        response = self.view(request, **kwargs)
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    def test_access_granted_published_article(self):
        comment_uid = self.test_comment2.uid
        article_slug = self.test_article2.slug
        kwargs = {"comment_uid": comment_uid, "article_slug": article_slug}
        url = reverse('main:comments:detail', kwargs=kwargs)
        request = self.factory.get(url)
        force_authenticate(request, user=self.test_author2)
        response = self.view(request, **kwargs)
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_access_granted_user_has_article_perm(self):
        comment_uid = self.test_comment1.uid
        article_slug = self.test_article1.slug
        kwargs = {"comment_uid": comment_uid, "article_slug": article_slug}
        url = reverse('beta:comments:detail', kwargs=kwargs)
        request = self.factory.get(url)
        force_authenticate(request, user=self.test_author1)
        response = self.view(request, **kwargs)
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_anonymous_user_denied(self):
        pass

    def test_anonymous_user_granted(self):
        pass


class CreateCommentAPITest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_article1 = ArticleFactory(title='test article 1', status='beta')
        cls.test_article2 = ArticleFactory(title='test article 2', status='published')
        cls.test_article3 = ArticleFactory(title='test article 3', status='archived')
        cls.test_author1 = cls.test_article1.author
        cls.test_author2 = cls.test_article2.author
        cls.test_author3 = cls.test_article3.author
        create_perms_and_groups_for_article(instance=cls.test_article1)
        create_perms_and_groups_for_article(instance=cls.test_article2)
        super_group1 = Group.objects.get(name=str(cls.test_article1.id) + FULL_ACCESS_SUFFIX)
        super_group2 = Group.objects.get(name=str(cls.test_article2.id) + FULL_ACCESS_SUFFIX)
        cls.test_author1.groups.add(super_group1)
        cls.test_author1.groups.add(super_group2)
        cls.factory = APIRequestFactory()
        cls.view = CommentCreateAPI.as_view()

    def test_permission_denied_article_status(self):
        article_slug = self.test_article3.slug
        kwargs = {"article_slug": article_slug}
        url = reverse('create', kwargs=kwargs)
        request = self.factory.post(url, {'contents': 'random contents1'})
        force_authenticate(request, user=self.test_author3)
        response = self.view(request, **kwargs)
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    def test_comment_created_properly_open_status(self):
        article_slug = self.test_article2.slug
        kwargs = {"article_slug": article_slug}
        url = reverse('create', kwargs=kwargs)
        request = self.factory.post(url, {'contents': 'random contents2'})
        force_authenticate(request, user=self.test_author1)
        response = self.view(request, **kwargs)
        self.assertEqual(response.status_code, HTTP_201_CREATED)

    def test_permission_denied_user_perms(self):
        # article_slug = self.test_article1.slug
        # kwargs = {"article_slug": article_slug}
        # url = reverse('create', kwargs=kwargs)
        # request = self.factory.post(url, {'contents': 'random contents2'})
        # force_authenticate(request, user=self.test_author2)
        # response = self.view(request, **kwargs)
        # self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)
        pass

    def test_comment_created_properly_user_has_perms(self):
        # article_slug = self.test_article2.slug
        # kwargs = {"article_slug": article_slug}
        # url = reverse('create', kwargs=kwargs)
        # request = self.factory.post(url, {'contents': 'random contents2'})
        # force_authenticate(request, user=self.test_author1)
        # response = self.view(request, **kwargs)
        # self.assertEqual(response.status_code, HTTP_200_OK)
        pass


class UpdateCommentAPITest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_article1 = ArticleFactory(title='test article 1', status='beta')
        cls.test_article2 = ArticleFactory(title='test article 2', status='published')
        cls.test_article3 = ArticleFactory(title='test article 3', status='archived')
        cls.test_author1 = cls.test_article1.author
        cls.test_author2 = cls.test_article2.author
        cls.test_author3 = cls.test_article3.author
        create_perms_and_groups_for_article(instance=cls.test_article1)
        create_perms_and_groups_for_article(instance=cls.test_article2)
        super_group1 = Group.objects.get(name=str(cls.test_article1.id) + FULL_ACCESS_SUFFIX)
        super_group2 = Group.objects.get(name=str(cls.test_article2.id) + FULL_ACCESS_SUFFIX)
        cls.test_author1.groups.add(super_group1)
        cls.test_author1.groups.add(super_group2)
        cls.test_comment1 = CommentFactory(author=cls.test_author1)
        cls.factory = APIRequestFactory()
        cls.view = CommentCreateAPI.as_view()

    def test_no_longer_editable_if_article_archived(self):
        kwargs = {'article_slug': self.test_article3.slug, 'comment_uid': self.test_comment1.uid}
        url = reverse('archived:comments:update', kwargs=kwargs)
        request = self.factory.patch(url, {'contents': 'updated contents'})

    def test_update_denied_not_author(self):
        pass

    def test_comment_properly_updated(self):
        pass


class DeleteCommentAPITest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_article1 = ArticleFactory(title='test article 1', status='beta')
        cls.test_article2 = ArticleFactory(title='test article 2', status='published')
        cls.test_author1 = cls.test_article1.author
        cls.test_author2 = cls.test_article2.author
        create_perms_and_groups_for_article(instance=cls.test_article1)
        create_perms_and_groups_for_article(instance=cls.test_article2)
        super_group1 = Group.objects.get(name=str(cls.test_article1.id) + FULL_ACCESS_SUFFIX)
        super_group2 = Group.objects.get(name=str(cls.test_article2.id) + FULL_ACCESS_SUFFIX)
        cls.test_author1.groups.add(super_group1)
        cls.test_author1.groups.add(super_group2)
        cls.test_comment1 = CommentFactory(author=cls.test_author1)
        cls.factory = APIRequestFactory()
        cls.view = CommentDeleteAPI.as_view()

    def test_denied_if_not_author(self):
        comment_uid = self.test_comment1.uid
        article_slug = self.test_article1.slug
        kwargs = {"comment_uid": comment_uid, "article_slug": article_slug}
        url = reverse('main:comments:delete', kwargs=kwargs)
        request = self.factory.delete(url)
        force_authenticate(request, user=self.test_author2)
        response = self.view(request, **kwargs)
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    def test_properly_deleted(self):
        pass

    def test_not_deleted_cause_has_children(self):
        pass
