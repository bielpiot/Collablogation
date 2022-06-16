from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase

from Collablogation.articles.tests.articles_factories import ArticleFactory
from .accounts_factories import UserFactory

User = get_user_model()


class GroupsAndPermissionCreationTest(TestCase):

    def setUp(self):
        self.test_article_1 = ArticleFactory(author__username='test_user_1', status='draft')
        self.test_user_2 = UserFactory(username='test_user_2')

    def test_group_and_perm_creation(self):
        test_user_1 = User.objects.get(username='test_user_1')
        test_user_2 = User.objects.get(username='test_user_2')
        id1 = self.test_article_1.uuid
        super_group_q = Group.objects.filter(name=f'{id1}_full_access_group')
        testers_group_q = Group.objects.filter(name=f'{id1}_testers_group')
        super_group = Group.objects.get(name=f'{id1}_full_access_group')
        suffixes = ['_can_view_permission',
                    '_can_edit_permission',
                    '_can_hook_inline_comments_permission',
                    '_can_delete_permission']
        perm_names = [f'{id1}{suffix}' for suffix in suffixes]

        # check groups being created
        self.assertEqual(testers_group_q.exists(), 1)
        self.assertEqual(super_group_q.exists(), 1)

        # assert correct and only one user in the group
        self.assertEqual(super_group.user_set.count(), 1)
        self.assertIn(test_user_1, super_group.user_set.all())
        self.assertNotIn(test_user_2, super_group.user_set.all())

        # assert permission existence
        for permission_name in perm_names:
            self.assertEqual(test_user_1.has_perm(permission_name), 1)
            self.assertEqual(test_user_2.has_perm(permission_name), 0)
