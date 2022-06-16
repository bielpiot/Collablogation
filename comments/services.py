from jsondiff import insert, delete, replace, diff as jdiff

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.exceptions import PermissionDenied, ValidationError

from .models import InlineComment, Comment
from .utils import get_all_keys_from_nested_json, merge_json_values_under_key
from ..articles.models import Article
from ..articles.perm_constants import view_permission, add_inline_comments_permission

User = get_user_model()

art_view_suffix, _ = view_permission


def modified_article_body_is_valid(*, base, modified):
    diff = jdiff(base, modified)
    text_base = merge_json_values_under_key(base, "text")
    text_modified = merge_json_values_under_key(modified, "text")

    condition1 = text_base == text_modified
    condition2 = delete not in diff


def inline_comment_create(*, user: User, post: Post, **kwargs) -> InlineComment:
    pass
    # validate related article partial edit permissions
    # triggering hook logic (validation, transaction atomic etc) only if no parent comment
    # transaction atomic: creating comment and modifying article (span/tree mod) simultaneously


def inline_comment_hook(*, article: Article, inline_comment: InlineComment):
    pass
    # if parent comment -> hook_id == parent_comment__id
    # special validation: compare input of related article body (contents)
    # cannot delete if has child comment(s)?
    # assuming we are storing slate.js document object: join everything under text and url
    # and check if no changes apparent + check whether only new json keys are comment_thread_hooks


def inline_comment_change(*, article: Article, inline_comment: InlineComment):
    # cannot change if it's been responded to
    pass


def inline_comment_delete():
    # If no child comments, delete, along with hook. If child comments, delete just the body.
    pass


def comment_validate_article_consistency(*, article: Article, parent_article: Article) -> None:
    if not article == parent_article:
        raise ValidationError('Cannot create comment with different article than parent comment')


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
    if parent_comment:
        comment_validate_article_consistency(article=article,
                                             parent_article=parent_comment.article)
    comment = Comment.objects.create(author=user, article=article, parent_comment=parent_comment, **kwargs)
    comment.full_clean()
    comment.save()
    return comment


def comment_change(*, user: User, article: Article, comment: Comment) -> None:
    # action not possible if comment has been answered (or is_staff, ofc)
    perm = article.id + art_view_suffix_suffix
    if (comment.has_children and not user.is_staff) or not user.has_article_perm(perm):
        raise PermissionDenied('You cannot modify this comment')
    comment = 1  # further operations


def comment_delete() -> None:
    # set body to "comment deleted"
    pass
