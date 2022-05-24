from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.exceptions import PermissionDenied

from .models import InlineComment, Comment
from ..articles.models import Article
from ..articles.perm_constants import view_permission

User = get_user_model()

art_view_suffix, _ = view_permission


def inline_comment_create(*, user=User, post=Post, **kwargs) -> InlineComment:
    pass
    # validate related article partial edit permissions


def inline_comment_hook():
    pass
    # if parent comment -> hook_id == parent_comment__id
    # special validation: compare input


def comment_create(*,
                   user: User,
                   article: Article,
                   parent_comment: Comment = None,
                   perm_suffix: str = art_view_suffix,
                   **kwargs
                   ) -> Comment:
    article_id = article.id
    codename = article_id + perm_suffix
    if not user.has_article_perm(codename):
        raise PermissionDenied()
    comment = Comment.objects.create(author=user, article=article, parent_comment=parent_comment, **kwargs)
    comment.full_clean()
    comment.save()
    return comment
