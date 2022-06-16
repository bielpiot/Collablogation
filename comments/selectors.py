from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.exceptions import PermissionDenied
from django.db.models.query import QuerySet

from .models import Comment, InlineComment
from ..articles.models import Article
from ..articles.perm_constants import view_permission
from ..api.utils import get_object

User = get_user_model()

art_view_suffix, _ = view_permission


def comment_list(*, user: User, article_id: str, perm_suffix: str = art_view_suffix) -> QuerySet[Comment]:
    codename = article_id + perm_suffix
    article = get_object(Article.objects.all().select_related('status'), pk=article_id)
    if not (user.has_article_perm(codename) or article.status == 'published'):
        raise PermissionDenied()
    qs = Article.objects.filter(id=article_id).comments.all()
    return qs


def comment_detail(*, user: User, comment_id: str, perm_suffix: str = art_view_suffix) -> Comment:
    comment = get_object(Comment.object.all().select_related('article'), pk=comment_id)
    article_id = comment.article_id
    codename = article_id + perm_suffix
    if not (user.has_article_perm(codename) or commment.article_status == 'published'):
        raise PermissionDenied()
    return comment


def inline_comment_thread(*, article: Article, hook_id: str) -> QuerySet:
    # returns queryset of all comments hooked to the same id order by creation date
    pass


def inline_comment_detail():
    pass
