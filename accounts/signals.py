from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Account
from .permission_names import article_permissions_pattern
from .utils import generate_groups_and_permissions
from articles.models import Article

User = get_user_model()


@receiver(post_save, sender=Article)
def create_groups_for_article(sender, instance, **kwargs):
    """ Building groups and permissions for created Article instance
        along with automatic group assignment for article author"""
    if kwargs['created']:
        content_type = ContentType.objects.get(model=instance._meta.model_name)
        generate_groups_and_permissions(instance_name=instance.id, permissions_pattern=article_permissions_pattern,
                                        content_type=content_type)
        super_group = Group.objects.get(name=instance.id + '_full_access')
        instance.author.groups.add(super_group)
    else:
        print('Article has not been created')


@receiver(post_save, sender=User)
def create_profile(sender, instance, **kwargs):
    if kwargs['created']:
        Account.objects.create(user=instance)
    else:
        print('User/account has not been created')
