from django.contrib.auth import get_user_model
from django.utils import timezone
from typing import Tuple
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from .models import Article
from .perm_constants import article_permissions_pattern, full_edit_permission, FULL_ACCESS_SUFFIX
from articles.utils import generate_groups_and_permissions
from api.utils import get_object

User = get_user_model()


def create_perms_and_groups_for_article(*, instance: Article, **kwargs) -> None:
    """ Building groups and permissions for created Article instance
        along with group assignment for article author"""
    content_type = ContentType.objects.get(model=instance._meta.model_name)
    generate_groups_and_permissions(instance_name=instance.id,
                                    permissions_pattern=kwargs.get('perm_pattern', article_permissions_pattern),
                                    content_type=content_type)
    super_group = Group.objects.get(name=str(instance.id) + FULL_ACCESS_SUFFIX)
    instance.author.groups.add(super_group)


def article_create(*, user: User, **kwargs):
    """all logic behind Article creation - restrictions, relations etc"""
    article = Article.objects.create(author=User, **kwargs)
    article.status = 'draft'
    create_perms_and_groups_for_article(instance=article)
    article.full_clean()
    article.save()
    return article


def clean_pre_publish_formatting(*, article: Article) -> Article:
    # remove all inline comments ->
    contents = article.contents
    pass


def article_publish(*, article: Article) -> Article:
    """
    Service modifying Post instance before publishing:

    """
    clean_pre_publish_formatting(article)
    article.status = 'published'
    article.published = timezone.now()
    article.full_clean()
    article.save()
    return article


def article_edit(*, article: Article, user: User) -> Article:
    """all logic behind Article edition - restrictions, relations etc"""
    pass


def article_delete(*, article: Article, user: User):
    """all logic behind Article deletion - restrictions, relations etc"""
    pass


def article_archive(*, article: Article, user: User) -> Article:
    pass
