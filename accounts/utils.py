from typing import Tuple

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


def generate_groups_and_permissions(*, instance_name: str,
                                    permissions_pattern: Tuple[str],
                                    content_type: ContentType) -> None:
    """Function generating groups along with permissions for instance given
       instance name (in most uses: instance id) and naming pattern (group and perms names)"""

    for group_name_pattern, permission_name_patterns in permissions_pattern.items():
        group_name = instance_name + group_name_pattern
        group = Group.objects.create(name=group_name)
        for permission_pattern in permission_name_patterns:
            permission_codename = instance_name + permission_pattern[0]
            permission_name = permission_pattern[1] + instance_name
            permission, created = Permission.objects.get_or_create(codename=permission_codename,
                                                                   name=permission_name,
                                                                   content_type=content_type)
            group.permissions.add(permission)
