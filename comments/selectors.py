from collections import defaultdict
from typing import List

from articles.models import Article
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.db.models.query import QuerySet
from django_filters import FilterSet

from .models import Comment, InlineComment

User = get_user_model()


class CommentFilter(FilterSet):
    class Meta:
        model = Comment
        fields = ('author',)


def comment_list(*, user: User,
                 article: Article,
                 perm_suffix: str = art_view_suffix,
                 filters=None) -> QuerySet[Comment]:
    filters = filters or {}
    article_id = article.id
    codename = str(article_id) + perm_suffix
    if not (user.has_article_perm(codename) or article.status == 'published'):
        raise PermissionDenied()
    qs = Article.objects.filter(id=article_id).order_by('-created')
    return CommentFilter(filters, qs).qs


def comments_by_thread(*, user: User, article: Article) -> List[List[Comment]]:
    qs = Comment.objects.filter(article=article).select_related('thread_id').order_by('-created')

    grouped = defaultdict(list)
    for comment in qs:
        grouped[comment.thread_id].append(comment)

    return list(grouped.values())


def comment_detail(*, user: User, comment: Comment) -> Comment:
    # placeholder, if some logic complication occurs in the future, operate here
    return comment


# returns inline comments thread
def inline_comment_thread(*, article: Article, thread_id: str) -> QuerySet:
    q = InlineComment.objects.filter(thread_id=thread_id).order_by('-created')
    pass


def inline_comment_detail(*, article: Article, inline_comment: InlineComment) -> InlineComment:
    # placeholder, if some logic complication occurs in the future, operate here
    return inline_comment
