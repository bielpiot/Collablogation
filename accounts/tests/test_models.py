from django.test import TestCase
from django.db import IntegrityError

from ..models import Follow
from .accounts_factories import AccountFactory


class FollowTest(TestCase):

    def setUp(self) -> None:
        test_account = AccountFactory()

    def test_follow_constraint(self):
        constraint_name = 'self_follow_restricted'
        with self.assertRaisesMessage(IntegrityError, constraint_name):
            Follow.objects.create(from_account=test_account, to_account=test_account)
