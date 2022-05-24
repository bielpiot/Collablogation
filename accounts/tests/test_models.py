from django.test import TestCase
from django.db import IntegrityError

from ..models import Follow
from .accounts_factories import UserFactory


class FollowTest(TestCase):

    def setUp(self):
        test_user = UserFactory()

    def test_follow_constraint(self):
        constraint_name = 'self_follow_restricted'
        with self.assertRaisesMessage(IntegrityError, constraint_name):
            Follow.objects.create(from_user=test_user, to_user=test_user)
