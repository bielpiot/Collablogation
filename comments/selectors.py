from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.exceptions import PermissionDenied
from django.db.models.query import QuerySet

from .models import Comment, InlineComment
from ..articles.models import Article
from ..articles.perm_constants import view_permission

User = get_user_model()

art_view_suffix, _ = view_permission


def comment_list(*, user: User, id: str, perm_suffix: str = art_view_suffix) -> QuerySet[Comment]:
    codename = id + perm_suffix
    if not user.has_article_perm(codename):
        raise PermissionDenied()
    return Article.objects.filter(uuid=id).comments.all()


def comment_detail(*, user: User, comment_id: str, perm_suffix: str = art_view_suffix) -> Comment:
    comment = Comment.objects.get(pk=comment_id).select_related('article')
    article_id = comment.article.uuid
    codename = article_id + perm_suffix
    if not user.has_article_perm(codename):
        raise PermissionDenied()
    return comment
