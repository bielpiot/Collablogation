from accounts.perm_constants import article_permissions_pattern
from accounts.tests.accounts_factories import UserFactory
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, ContentType
from django.test import TestCase

from .articles_factories import ArticleFactory
from ..utils import generate_groups_and_permissions

User = get_user_model()


class GroupsAndPermissionCreationTest(TestCase):

    def setUp(self):
        self.test_article_1 = ArticleFactory(status='draft')
        self.test_user_2 = UserFactory()
        generate_groups_and_permissions(instance_name=self.test_article_1.id,
                                        permissions_pattern=article_permissions_pattern,
                                        content_type=ContentType.objects.get(app_label='articles',
                                                                             model='article'))

    def test_generate_groups_and_permissions(self):
        test_user_1 = self.test_article_1.author
        test_user_2 = self.test_user_2
        id1 = self.test_article_1.id
        super_group_q = Group.objects.filter(name=f'{id1}_full_access')
        testers_group_q = Group.objects.filter(name=f'{id1}_testers')
        super_group = Group.objects.get(name=f'{id1}_full_access')

        # check groups being created
        self.assertEqual(testers_group_q.exists(), 1)
        self.assertEqual(super_group_q.exists(), 1)

        # assert correct and only one user in the group
        self.assertEqual(super_group.user_set.count(), 1)
        self.assertIn(test_user_1, super_group.user_set.all())
        self.assertNotIn(test_user_2, super_group.user_set.all())
