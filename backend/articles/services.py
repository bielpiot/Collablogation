from typing import Any, Dict

from accounts.perm_constants import article_permissions_pattern, FULL_ACCESS_SUFFIX
from common.services import model_update
from common.utils import generate_groups_and_permissions
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.utils import timezone

from .models import Article

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


def remove_users_from_article_perm_groups(*, article: Article):
    """Service responsible for cleaning groups and perms for given article, typically used when deleting/archiving."""
    id = str(article.id)
    author = article.author
    article_groups = Group.objects.filter(codename__startswith=id)
    for grp in article_groups:
        grp.user_set.remove()


@transaction.atomic
def article_create(*, user: User, **kwargs):
    """Service responsible for article instance creation, extended by other changes required by business logic"""
    article = Article.objects.create(author=user, **kwargs)
    article.status = Article.DRAFT
    article.full_clean()
    article.save()
    create_perms_and_groups_for_article(instance=article)
    return article


def clean_pre_publish_formatting(*, article: Article) -> Article:
    """Cleaning formatting that is redundant once article is published"""
    # remove all inline comments -> join() util to be implemented, basically concatenating
    # adjacent text nodes with common formatting arguments (after given thread_ removal)
    # contents = article.contents
    # remove_users_from_article_perm_groups(article=article)
    pass


def article_delete(*, article: Article, user: User):
    """Service responsible for article deletion along with other data changes required by business logic"""
    if article.status == Article.PUBLISHED:
        raise PermissionError('This resource cannot be deleted!')
    article.delete()


@transaction.atomic
def article_update(*, article: Article,
                   data: Dict[str, Any]
                   ) -> Article:
    """Service responsible for proper article instance update, along with extended changes required by business logic"""
    old_status = getattr(article, 'status')
    status = data.get('status', old_status)
    status_has_changed = (old_status != status)
    fields = ['contents', 'status', 'category', 'title']
    if 'tags' in data:
        for tag in data['tags']:
            article.tags.add(tag)
    if status == Article.PUBLISHED and status_has_changed:
        data['publish_date'] = timezone.now()
        fields.append('publish_date')
        # clean_pre_publish_formatting(article=article) TODO add when hooking beta section
    updated_article, was_updated = model_update(instance=article, fields=fields, data=data)
    # if not was_updated:
    #     return article
    return updated_article
