from typing import Tuple
from uuid import uuid4 as uuid

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import serializers


def create_serializer_class(name, fields):
    """source : Hacksoftware Django styleguide"""
    return type(name, (serializers.Serializer,), fields)


def inline_serializer(*, fields, data=None, **kwargs):
    """source : Hacksoftware Django styleguide"""
    serializer_class = create_serializer_class(name='', fields=fields)

    if data is not None:
        return serializer_class(data=data, **kwargs)

    return serializer_class(**kwargs)


def get_object(model_or_queryset, **kwargs):
    """return None in case of 404"""
    try:
        return get_object_or_404(model_or_queryset, **kwargs)
    except Http404:
        return None


def generate_groups_and_permissions(*, instance_name: uuid,
                                    permissions_pattern: Tuple[str],
                                    content_type: ContentType) -> None:
    """Function generating groups along with permissions for instance given
       instance name (in most uses: instance id) and naming pattern (group and perms names)"""

    for group_name_pattern, permission_name_patterns in permissions_pattern.items():
        group_name = str(instance_name) + group_name_pattern
        group = Group.objects.create(name=group_name)
        for permission_pattern in permission_name_patterns:
            permission_codename = str(instance_name) + permission_pattern[0]
            permission_name = permission_pattern[1] + str(instance_name)
            permission, created = Permission.objects.get_or_create(codename=permission_codename,
                                                                   name=permission_name,
                                                                   content_type=content_type)
            group.permissions.add(permission)
