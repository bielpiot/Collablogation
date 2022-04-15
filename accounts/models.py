import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone

from articles.models import Article


class UserManager(BaseUserManager):

    def create_user(self, username, email, password=None):
        if username is None:
            raise TypeError('Please provide username.')
        if email is None:
            raise TypeError('Please provide email')

        user = self.model(
            username=username,
            email=self.normalize_email(email))

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
        user = self.create_user(username, email, password)
        user.is_superuser = True
        user.is_staff = True
        user.full_clean()
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    uuid = models.UUIDField(primary_key=True, db_index=True, default=uuid.uuid4)
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(max_length=255, unique=True, db_index=True, verbose_name='email address')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now, editable=False)
    last_update = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username


class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    about = models.CharField(max_length=300, blank=True, null=True)
    contact = models.CharField(max_length=300, blank=True, null=True)
    followers = models.ManyToManyField(to='self', related_name='followed_by', through='Follow', null=True,
                                       symmetrical=False)
    favourite_posts = models.ManyToManyField(Article, related_name='liked_by', null=True)


class Follow(models.Model):
    from_account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="+")
    to_account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="+")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='%(class)s_relationships_to_be_unique',
                fields=["from_account", "to_account"],
            ),
            models.CheckConstraint(
                name='self_%(class)s_restricted',
                check=~models.Q(from_account=models.F('to_account'))
            )
        ]
