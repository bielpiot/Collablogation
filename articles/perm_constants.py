# mapping for permissions and permission groups
view_permission = ('_can_view_permission', 'Can view ')
full_edit_permission = ('_can_edit_permission', 'Can edit ')
add_inline_comments_permission = ('_can_hook_inline_comments_permission', 'Can hook inline comments in ')
delete_permission = ('_can_delete_permission', 'Can delete ')

full_permissions = [view_permission, full_edit_permission, delete_permission, add_inline_comments_permission]
testers_permissions = [view_permission, add_inline_comments_permission]

FULL_ACCESS_SUFFIX = '_full_access'
TESTERS_SUFFIX = '_testers'

article_permissions_pattern = {
    FULL_ACCESS_SUFFIX: full_permissions,
    TESTERS_SUFFIX: testers_permissions,
}
