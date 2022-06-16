from django.contrib.auth.models import Group, Permission
from .articles_factories import ArticleFactory
from ..perm_constants import view_permission


class CreatePermsAndGroupsForArticleTest(TestCase):
    def setUp(self) -> None:
        self.test_article1 = ArticleFactory()
        self.test_article2 = ArticleFactory()
        self.test_author1 = self.test_article1.author
        self.test_author2 = self.test_article2.author

    def test_group_perms_and_assignment_process(self):
        codename, _ = view_permission
        self.assertEqual(Group.objects.all().count(), 0)
        create_perms_and_groups_for_article(instance=self.test_article1.id)
        view_perm = self.test_article1.id + codename
        self.assertEqual(Group.objects.all().count(), 1)
        self.assertEqual(self.test_author1.has_article_perm(view_perm), True)
        self.assertEqual(self.test_author2.has_article_perm(view_perm), False)


class ArticleCreateTest(TestCase):
    pass
