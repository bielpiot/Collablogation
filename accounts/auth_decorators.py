from functools import wraps
from typing import Tuple

from articles.models import Article
# from common.utils import get_object
from django.core.exceptions import PermissionDenied


def article_status_or_permission_required(*, permission: Tuple = None, status: Tuple = None):
    """Function establishing access for article/article related resource.
       If used, access for resource is denied by default and given permission or tuple containing
       statuses are only exceptions under which access is granted
    """

    def decorator(drf_view):
        @wraps(drf_view)
        def _wrapped(request, *args, **kwargs):
            article_slug = kwargs.get("article_slug")
            # article = get_object(Article, slug=article_slug) for some reason doesnt get object??
            article = Article.objects.get(slug=article_slug)
            perm_condition = False
            status_condition = False
            message = kwargs.get('access_message', 'Action not allowed')
            if permission and request.user.is_authenticated:
                try:
                    suffix, _ = permission
                    perm = str(article.id) + suffix
                    perm_condition = request.user.is_authenticated and request.user.has_article_perm(perm=perm)
                except AttributeError:
                    perm_condition = perm_condition
            if status:
                status_condition = article.status in status

            if perm_condition or status_condition:
                return drf_view(request, *args, **kwargs)
            else:
                raise PermissionDenied(message)

        return _wrapped

    return decorator


def article_status_and_permission_required(*, permission: Tuple = None, status: Tuple = None):
    """Function establishing access for article/article related resource.
       If used, access for resource is denied by default and given permission or tuple containing
       statuses are only exceptions under which access is granted
    """

    def decorator(drf_view):
        @wraps(drf_view)
        def _wrapped(request, *args, **kwargs):
            article_slug = kwargs.get("article_slug")
            # article = get_object(Article, slug=article_slug)
            article = Article.objects.get(slug=article_slug)
            perm_condition = True
            status_condition = True
            message = kwargs.get('access_message', 'Action not allowed')
            if permission:
                try:
                    suffix, _ = permission
                    perm = str(article.id) + suffix
                    perm_condition = request.user.is_authenticated and request.user.has_article_perm(perm=perm)
                except AttributeError:
                    perm_condition = False
            if status:
                status_condition = article.status in status

            if perm_condition and status_condition:
                return drf_view(request, *args, **kwargs)
            else:
                raise PermissionDenied(message)

        return _wrapped

    return decorator
