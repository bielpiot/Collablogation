from typing import Any, Dict

from articles.utils import generate_groups_and_permissions
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from .models import Article
from .perm_constants import article_permissions_pattern, FULL_ACCESS_SUFFIX

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
    """"""
    id = str(article.id)
    author = article.author
    article_groups = Group.objects.filter(codename__startswith=id)
    for grp in article_groups:
        grp.user_set.remove()


def article_create(*, user: User, **kwargs):
    """all logic behind Article creation - restrictions, relations etc"""
    article = Article.objects.create(author=User, **kwargs)
    article.status = 'draft'
    create_perms_and_groups_for_article(instance=article)
    article.full_clean()
    article.save()
    return article


def clean_pre_publish_formatting(*, article: Article) -> Article:
    # remove all inline comments -> join() util to be implemented, basically concatenating
    # adjacent text nodes with common formatting arguments (after given thread_ removal)
    # contents = article.contents
    # remove_users_from_article_perm_groups(article=article)
    pass


def article_archive(*, article: Article) -> Article:
    """
    Can be performed on published/beta article.
    Article becomes uneditable, access only for full access group members, read only
    """
    article.frozen = True
    return article


def article_publish(*, article: Article) -> Article:
    """
    Service modifying Post instance before publishing:

    """
    # clean_pre_publish_formatting(article=article)
    article.published = timezone.now()
    return article


def article_delete(*, article: Article, user: User):
    """all logic behind Article deletion - restrictions, relations etc.
    Cannot be performed on published article
    remove all users from access groups except author?
    """
    article.delete()


def article_update(*, article: Article,
                   user: User,
                   data: Dict[str, Any]
                   ) -> Article:
    """all logic behind Article edition - restrictions, relations etc"""
    # TODO transaction atomic for series of changes like publishing then updating etc
    if article.frozen:
        raise PermissionError('This resource cannot be modified anymore')
    status = data.get('status', None)
    if status == Article.ARCHIVED:
        article_archive(article=article)
    if status == Article.PUBLISHED:
        article_publish(article=article)
    updated_article, was_updated = model_update(instance=article, fields=fields, data=data)
    return updated_article
