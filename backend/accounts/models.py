import uuid

from articles.models import Article
from django.contrib import auth
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import PermissionDenied
from django.db import models
from django.utils import timezone
from versatileimagefield.fields import VersatileImageField


def _user_has_article_perm(user, perm):
    """
    A backend can raise `PermissionDenied` to short-circuit permission checking.
    """
    for backend in auth.get_backends():
        if not hasattr(backend, "has_article_perm"):
            continue
        try:
            if backend.has_article_perm(user, perm):
                return True
        except PermissionDenied:
            return False
    return False


class UserManager(BaseUserManager):

    def create_user(self, username, email, password=None, is_active=False):
        if username is None:
            raise TypeError('Please provide username.')
        if email is None:
            raise TypeError('Please provide email')

        user = self.model(
            username=username,
            email=self.normalize_email(email),
            is_active=is_active)

        if password is not None:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.full_clean()
        user.save()

        return user

    def create_superuser(self, username, email, password):
        if password is None:
            raise TypeError('Please provide password')
        user = self.create_user(username, email, password, is_active=True)
        user.is_superuser = True
        user.is_staff = True
        user.full_clean()
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, db_index=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(max_length=255, unique=True, db_index=True, verbose_name='email address')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now, editable=False)
    last_update = models.DateTimeField(auto_now=True)
    avatar = VersatileImageField(blank=True, null=True)
    about = models.CharField(max_length=300, blank=True, null=True)
    contact = models.CharField(max_length=300, blank=True, null=True)
    followers = models.ManyToManyField(to='self', related_name='followed_by', through='Follow',
                                       symmetrical=False)
    favourite_posts = models.ManyToManyField(Article, related_name='liked_by')

    objects = UserManager()

    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username

    def has_article_perm(self, perm):
        if self.is_active and self.is_superuser:
            return True
        return _user_has_article_perm(self, perm)


class Follow(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="+")
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="+")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='%(class)s_relationships_to_be_unique',
                fields=["from_user", "to_user"],
            ),
            models.CheckConstraint(
                name='self_%(class)s_restricted',
                check=~models.Q(from_user=models.F('to_user'))
            )
        ]
