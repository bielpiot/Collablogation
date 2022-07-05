from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import Permission
from django.contrib.auth import get_user_model
from django.db.models import Q


class ArticleBackend(ModelBackend):
    '''
    A Backend class processing per-article instance permissions
    '''

    def _get_user_article_permissions(self, user_obj, article):
        codename_pref = str(article.id)
        return user_obj.user_permissions.filter(codename__startswith=codename_pref)

    def _get_group_article_permissions(self, user_obj, article):

        user_groups_field = get_user_model()._meta.get_field('groups')
        user_groups_query = f'group__{user_groups_field.related_query_name()}'
        article_id = str(article.id)
        return Permission.objects.filter(
            **{user_groups_query: user_obj},
            codename__startswith=article_id)

    def _get_article_permissions(self, user_obj, article, from_name):
        '''
        Following predecessor's logic, generic rule for both group and
        user permissions (derived by specifying from name)
        '''
        if not user_obj.is_active or user_obj.is_anonymous:
            return set()

        perm_cache_name = f'_{from_name}_article_{article.id}_perm_cache'
        if not hasattr(user_obj, perm_cache_name):
            if user_obj.is_superuser:
                perms = Permission.objects.all()
            else:
                perms = getattr(self, f"_get_{from_name}_article_permissions")(user_obj, article)
            perms = perms.values_list('codename', flat=True).order_by()
            setattr(user_obj, perm_cache_name, {f'{name}' for name in perms})
        return getattr(user_obj, perm_cache_name)

    def get_user_article_permissions(self, user_obj, article):
        return self._get_article_permissions(user_obj, article, 'user')

    def get_group_article_permissions(self, user_obj, article):
        """
        Return a set of permission strings the user `user_obj` has from the
        groups they belong.
        """
        return self._get_article_permissions(user_obj, article, 'group')

    def get_all_article_permissions(self, user_obj, article):
        return {
            *self.get_user_article_permissions(user_obj, article),
            *self.get_group_article_permissions(user_obj, article),
            # *self.get_user_permissions(user_obj),
            # *self.get_group_permissions(user_obj),
        }

    def has_article_perm(self, user_obj, perm, article):
        return perm in self.get_all_article_permissions(user_obj, article)
