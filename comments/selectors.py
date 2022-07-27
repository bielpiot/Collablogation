from collections import defaultdict
from typing import List, Dict

from articles.models import Article
from django.contrib.auth import get_user_model

from .models import Comment, InlineComment

User = get_user_model()


def comment_belongs_to_article(*, comment: Comment, article: Article) -> bool:
    if comment not in article.comments.all():
        return False
    return True


def comments_list_by_thread(*, article: Article) -> List[List[Comment]]:
    qs = Comment.objects.filter(article=article).select_related('thread_id').order_by('-created')

    grouped = defaultdict(list)
    for comment in qs:
        grouped[comment.thread_id].append(comment)

    return list(grouped.values())


def comment_detail(*, user: User, comment: Comment) -> Comment:
    # placeholder for some potential logic
    return comment


# returns inline comments thread
def inline_comment_list_by_thread(*, article: Article) -> Dict[str, List[InlineComment]]:
    qs = InlineComment.objects.filter(article=article).select_related('thread_id').order_by('-created')

    grouped = defaultdict(list)
    for inline_comment in qs:
        grouped[inline_comment.thread_id].append(inline_comment)

    return grouped


def inline_comment_detail(*, article: Article, inline_comment: InlineComment) -> InlineComment:
    # placeholder, if some logic complication occurs in the future, operate here
    return inline_comment

