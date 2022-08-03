from accounts.tests.accounts_factories import UserFactory
from articles.apis import ArticleListAPI, ArticleDetailAPI, ArticleCreateAPI, ArticleUpdateAPI, ArticleDeleteAPI
from articles.models import Article
from articles.services import create_perms_and_groups_for_article
from django.shortcuts import reverse
from rest_framework.status import HTTP_403_FORBIDDEN, HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate

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
        cls.factory = APIRequestFactory()
        cls.view = ArticleListAPI.as_view()

    def test_drafts_lists(self):
        url = reverse('drafts:list')
        request = self.factory.get(url)
        force_authenticate(request, user=self.test_author1)
        response = self.view(request, **kwargs)
        self.assertEqual(len(response.data), 2)

    def test_beta_lists(self):
        url = reverse('beta:list')
        request = self.factory.get(url)
        force_authenticate(request, user=self.test_author3)
        response = self.view(request, **kwargs)
        self.assertEqual(len(response.data), 2)

    def test_published_lists(self):
        url = reverse('main:list')
        request = self.factory.get(url)
        response = self.view(request, **kwargs)
        self.assertEqual(len(response.data), 1)

    def test_archived_lists(self):
        url = reverse('archived:list')
        request = self.factory.get(url)
        force_authenticate(request, user=self.test_author2)
        response = self.view(request, **kwargs)
        self.assertEqual(len(response.data), 2)


class ArticleDetailAPITest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_author1 = UserFactory()
        cls.test_author2 = UserFactory()
        cls.test_article1 = ArticleFactory(status='draft', author=cls.test_author1)
        cls.test_article2 = ArticleFactory(status='published', author=cls.test_author1)
        cls.test_article3 = ArticleFactory(status='beta', author=cls.test_author1)
        cls.test_article4 = ArticleFactory(status='archived', author=cls.test_author1)
        create_perms_and_groups_for_article(instance=cls.test_article1)
        create_perms_and_groups_for_article(instance=cls.test_article3)
        create_perms_and_groups_for_article(instance=cls.test_article4)
        cls.factory = APIRequestFactory()
        cls.view = ArticleDetailAPI.as_view()

    def test_access_denied_draft_no_perm(self):
        kwargs = {'article_slug': self.test_article1.slug}
        url = reverse('drafts:detail', kwargs=kwargs)
        request = self.factory.get(url)
        force_authenticate(request, user=self.test_author2)
        response = self.view(request, **kwargs)
        self.assertEqual(response.status, HTTP_403_FORBIDDEN)

    def test_access_granted_draft_author(self):
        kwargs = {'article_slug': self.test_article1.slug}
        url = reverse('drafts:detail', kwargs=kwargs)
        request = self.factory.get(url)
        force_authenticate(request, user=self.test_author1)
        response = self.view(request, **kwargs)
        self.assertEqual(response.status, HTTP_200_OK)

    def test_access_granted_beta_with_perms(self):
        kwargs = {'article_slug': self.test_article3.slug}
        url = reverse('beta:detail', kwargs=kwargs)
        request = self.factory.get(url)
        force_authenticate(request, user=self.test_author1)
        response = self.view(request, **kwargs)
        self.assertEqual(response.status, HTTP_200_OK)

    def test_access_denied_beta_no_perms(self):
        kwargs = {'article_slug': self.test_article3.slug}
        url = reverse('beta:detail', kwargs=kwargs)
        request = self.factory.get(url)
        force_authenticate(request, user=self.test_author2)
        response = self.view(request, **kwargs)
        self.assertEqual(response.status, HTTP_403_FORBIDDEN)

    def test_access_archived_author(self):
        kwargs = {'article_slug': self.test_article4.slug}
        url = reverse('archived:detail', kwargs=kwargs)
        request = self.factory.get(url)
        force_authenticate(request, user=self.test_author1)
        response = self.view(request, **kwargs)
        self.assertEqual(response.status, HTTP_200_OK)

    def test_access_denied_archived_other_author(self):
        kwargs = {'article_slug': self.test_article4.slug}
        url = reverse('archived:detail', kwargs=kwargs)
        request = self.factory.get(url)
        force_authenticate(request, user=self.test_author2)
        response = self.view(request, **kwargs)
        self.assertEqual(response.status, HTTP_403_FORBIDDEN)

    def test_free_access_for_published_article(self):
        kwargs = {'article_slug': self.test_article2.slug}
        url = reverse('main:detail', kwargs=kwargs)
        request = self.factory.get(url)
        response = self.view(request, **kwargs)
        self.assertEqual(response.status, HTTP_200_OK)


class ArticleCreateAPITest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_author1 = UserFactory()
        cls.factory = APIRequestFactory()
        cls.view = ArticleCreateAPI.as_view()

    def test_article_created(self):
        self.assertEqual(Article.objects.all().exists(), 0)
        url = reverse('create')
        data = {'title': 'random title 1', 'contents': 'content1', 'tags': ['test']}
        request = self.factory.post(url, data)
        force_authenticate(request, user=self.test_author1)
        response = self.view(request)
        self.assertEqual(Article.objects.all().exists(), 1)
        self.assertEqual(response.status, HTTP_201_CREATED)

    def test_article_not_created_when_anonymous_user(self):
        url = reverse('create')
        data = {'title': 'random title 2', 'contents': 'content2', 'tags': ['test2']}
        request = self.factory.post(url, data)
        response = self.view(request)
        # self.assertEqual()


class ArticleUpdateAPITest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_author1 = UserFactory()
        cls.test_author2 = UserFactory()
        cls.test_author3 = UserFactory()
        cls.test_author4 = UserFactory()
        cls.test_article1 = ArticleFactory(status='draft', author=cls.test_author1)
        cls.test_article2 = ArticleFactory(status='published', author=cls.test_author2)
        cls.test_article3 = ArticleFactory(status='beta', author=cls.test_author3)
        cls.test_article4 = ArticleFactory(status='archived', author=cls.test_author4)
        create_perms_and_groups_for_article(instance=cls.test_article1)
        create_perms_and_groups_for_article(instance=cls.test_article2)
        create_perms_and_groups_for_article(instance=cls.test_article3)
        create_perms_and_groups_for_article(instance=cls.test_article4)
        cls.factory = APIRequestFactory()
        cls.view = ArticleUpdateAPI.as_view()

    def test_archived_article_can_no_longer_be_updated(self):
        kwargs = {'article_slug': self.test_article4.slug}
        url = reverse('archived:update', kwargs=kwargs)
        data = {'contents': 'updated contents'}
        request = self.factory.patch(url, data)
        force_authenticate(request, user=self.test_author4)
        response = self.view(request, **kwargs)
        self.assertEqual(response.status, HTTP_403_FORBIDDEN)

    def test_published_article_can_no_longer_be_updated(self):
        kwargs = {'article_slug': self.test_article2.slug}
        url = reverse('main:update', kwargs=kwargs)
        data = {'contents': 'updated contents'}
        request = self.factory.patch(url, data)
        force_authenticate(request, user=self.test_author2)
        response = self.view(request, **kwargs)
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    def test_update_draft_proper(self):
        kwargs = {'article_slug': self.test_article1.slug}
        url = reverse('main:update', kwargs=kwargs)
        data = {'contents': 'updated contents'}
        request = self.factory.patch(url, data)
        force_authenticate(request, user=self.test_author1)
        response = self.view(request, **kwargs)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(self.test_article1.contents, 'updated contents')

    def update_beta_denied_no_perm(self):
        kwargs = {'article_slug': self.test_article3.slug}
        url = reverse('main:update', kwargs=kwargs)
        data = {'contents': 'updated contents'}
        request = self.factory.patch(url, data)
        force_authenticate(request, user=self.test_author3)
        response = self.view(request, **kwargs)
        self.assertEqual(response.status, HTTP_200_OK)
        self.assertEqual(self.test_article1.contents, 'updated contents')


class ArticleDeleteAPITest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_author1 = UserFactory()
        cls.test_author2 = UserFactory()
        cls.test_article1 = ArticleFactory(status='draft', author=cls.test_author1)
        cls.test_article2 = ArticleFactory(status='published', author=cls.test_author2)
        create_perms_and_groups_for_article(instance=cls.test_article1)
        create_perms_and_groups_for_article(instance=cls.test_article2)
        cls.factory = APIRequestFactory()
        cls.view = ArticleDeleteAPI.as_view()

    def test_delete_published_article_not_allowed(self):
        kwargs = {'article_slug': self.test_article2.slug}
        url = reverse('main:delete', kwargs=kwargs)
        request = self.factory.delete(url)
        force_authenticate(request, user=self.test_author2)
        response = self.view(request, **kwargs)
        self.assertEqual(response.status, HTTP_403_FORBIDDEN)
        self.assertEqual(Article.objects.all().count(), 2)

    def test_article_deleted(self):
        kwargs = {'article_slug': self.test_article1.slug}
        url = reverse('main:delete', kwargs=kwargs)
        request = self.factory.delete(url)
        force_authenticate(request, user=self.test_author1)
        response = self.view(request, **kwargs)
        self.assertEqual(response.status, HTTP_204_NO_CONTENT)
        self.assertEqual(Article.objects.all().count(), 1)
