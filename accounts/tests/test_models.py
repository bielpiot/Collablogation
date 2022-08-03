from django.db import IntegrityError
from django.test import TestCase

from .accounts_factories import UserFactory
from ..models import Follow


class FollowTest(TestCase):

    def setUp(self):
        self.test_user = UserFactory()

    def test_follow_constraint(self):
        constraint_name = 'self_follow_restricted'
        with self.assertRaisesMessage(IntegrityError, constraint_name):
            Follow.objects.create(from_user=self.test_user, to_user=self.test_user)
