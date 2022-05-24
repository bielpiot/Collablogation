from django.contrib.auth import get_user_model
from django.utils import timezone
from typing import Tuple
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from .models import Article
from .perm_constants import article_permissions_pattern, full_permissions
from ..accounts.utils import generate_groups_and_permissions

User = get_user_model()


def create_perms_and_groups_for_article(*, instance: Article, **kwargs) -> None:
    """ Building groups and permissions for created Article instance
        along with group assignment for article author"""
    content_type = ContentType.objects.get(model=instance._meta.model_name)
    generate_groups_and_permissions(instance_name=instance.id,
                                    permissions_pattern=kwargs.get(perm_pattern, default=article_permissions_pattern),
                                    content_type=content_type)
    codename_suffix, _ = full_permissions
    super_group = Group.objects.get(name=instance.id + codename_suffix)
    instance.author.groups.add(super_group)


def article_create(*, user: User, **kwargs):
    article = Article.objects.create(author=User, **kwargs)
    article.status = 'draft'
    create_perms_and_groups_for_article(instance=article)
    article.full_clean()
    article.save()
    return article


def article_publish(*, article: Article) -> Article:
    """
    Service modifying Post instance before publishing:
    1. clear all <span> elements serving as hooks for inline comments
    """
    Article.status = 'published'
    Article.published = timezone.now()
