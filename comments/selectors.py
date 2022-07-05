from collections import defaultdict
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.db.models.query import QuerySet

from .models import Comment, InlineComment
from ..articles.models import Article
from ..articles.perm_constants import view_permission
from Collablogation.common.utils import get_object

User = get_user_model()

art_view_suffix, _ = view_permission


def comments_by_thread(*, user: User, article: Article) -> List[List[Comment]]:
    qs = Comment.objects.filter(article=article).select_related('thread_id').order_by('-created')

    grouped = defaultdict(list)
    for comment in qs:
        grouped[comment.thread_id].append(comment)

    return list(grouped.values())


def comment_list(*, user: User, article: Article, perm_suffix: str = art_view_suffix) -> QuerySet[Comment]:
    article_id = article.id
    codename = str(article_id) + perm_suffix
    if not (user.has_article_perm(codename) or article.status == 'published'):
        raise PermissionDenied()
    qs = Article.objects.filter(id=article_id).comments.all()
    return qs


def comment_detail(*, user: User, comment_id: str, perm_suffix: str = art_view_suffix) -> Comment:
    article_id = comment.article_id
    codename = str(article_id) + perm_suffix
    if not (user.has_article_perm(codename) or commment.article_status == 'published'):
        raise PermissionDenied()
    return comment


def inline_comment_thread(*, article: Article, thread_id: str) -> QuerySet:
    # returns queryset of all comments with commont thread_id
    q = InlineComment.objects.filter(thread_id=thread_id).order_by('-created')
    pass


def inline_comment_detail():
    pass
