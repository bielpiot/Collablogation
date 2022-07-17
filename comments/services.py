from typing import Iterable, Dict, Any

from articles.models import Article
from common.services import model_update
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction

from .models import InlineComment, Comment
from .utils import (merge_iterable_values_under_key,
                    group_nodes_by_matching_string_values,
                    trim_two_iterables_from_common_values,
                    get_nodes_with_given_key,
                    remove_nodes_with_given_key)

User = get_user_model()


def comment_validate_article_consistency(*, article: Article, parent_article: Article) -> None:
    if not article == parent_article:
        raise ValidationError('Cannot create comment with different article than parent comment')


def comment_freeze(*, comment: Comment):
    comment.contents = 'Comment deleted'
    comment.frozen = True
    comment.save()
    return comment


def comment_create(*,
                   user: User,
                   article: Article,
                   parent_comment: Comment = None,
                   **kwargs
                   ) -> Comment:
    if parent_comment:
        comment_validate_article_consistency(article=article,
                                             parent_article=parent_comment.article)
    comment = Comment.objects.create(author=user, article=article, parent_comment=parent_comment, **kwargs)
    comment.full_clean()
    comment.save()
    return comment


def comment_update(*,
                   user: User,
                   comment: Comment,
                   data: Dict[str, Any]
                   ) -> Comment:
    # action not possible if comment has been answered (or is_staff, ofc)
    if comment.has_children or not user == comment.author or comment.frozen:
        raise PermissionDenied('You cannot modify this comment')
    updated_comment, was_updated = model_update(instance=comment, fields=fields, data=data)
    if not was_updated:
        pass
    return updated_comment


def comment_delete(*, user: User, comment: Comment):
    if not user == comment.author or comment.frozen:
        raise PermissionDenied("Action not allowed")
    if comment.has_children:
        freeze_comment(comment=comment)
    else:
        comment.delete()


def split_nodes_are_valid(*, base: Iterable, modified: Iterable, inline_comment_id: str) -> bool:
    """
    Given two lists of text nodes verify if modified one reflects base one after performing
    splits necessary to anchor inline comment. Process goes like that:
    1. extract text nodes from iterable tree (nested json)
    2. trim list of text nodes from common nodes - we are interested only on part that is changing
    3. group modified nodes to match input nodes
    4. validate whether nothing is being added or removed (with exception of text itself and inline comment anchor
    """
    base_text_nodes = get_nodes_with_given_key(iterable=base, filter_key="text")
    modified_text_nodes = get_nodes_with_given_key(iterable=modified, filter_key="text")
    base_trimmed, modified_trimmed = trim_two_iterables_from_common_values(
        base=base_text_nodes, modified=modified_text_nodes
    )
    modified_trimmed_grouped = group_nodes_by_matching_string_values(base=base_trimmed,
                                                                     modified=modified_trimmed,
                                                                     filter_key="text")

    for compared, to_be_equal in zip(base_trimmed, modified_trimmed_grouped):
        node = {k: v for k, v in compared.items() if k != "text"}
        for split in to_be_equal:
            split_node = {k: v for k, v in split.items() if k not in ("text", f"thread_{inline_comment_id}")}
            if not node == split_node:
                return False
    return True


def modified_article_body_is_valid(*, base: Iterable, modified: Iterable, inline_comment_id: str) -> bool:
    """
    Compare two json iterables representing Article contents. Validates modified node against
    already existing in base. Checks if only allowed changes were made - that is, those connected
    to anchoring inline comment
    """
    text_base = merge_iterable_values_under_key(iterable=base, filter_key="text")
    text_modified = merge_iterable_values_under_key(iterable=modified, filter_key="text")
    rest_base = remove_nodes_with_given_key(iterable=base, filter_key="text")
    rest_modified = remove_nodes_with_given_key(iterable=modified, filter_key="text")
    split_nodes_valid = split_nodes_are_valid(base=base,
                                              modified=modified,
                                              inline_comment_id=inline_comment_id)

    condition1 = text_base == text_modified
    condition2 = rest_base == rest_modified
    condition3 = split_nodes_valid
    return condition1 and condition2 and condition3


def inline_comment_create(*,
                          user: User,
                          article_id: str,
                          parent_comment: InlineComment = None,
                          modified_article_contents: Iterable = None,
                          **kwargs) -> InlineComment:
    article = Article.objects.select_for_update().filter(id=article_id)

    if parent_comment:
        comment_validate_article_consistency(article=article, parent_article=parent_comment.article)
        if not modified_article_body_is_valid(base=article_conents, modified=modified_article_contents):
            raise ValidationError("Disallowed changes made in article contents!")

    with transaction.atomic():
        article.contents = modified_article_contents
        # TODO mind the json processing - dumps/loads etc. More steps potentially needed.
        article.full_clean()
        article.save()
        inline_comment = InlineComment.objects.create(user=user, article=article,
                                                      parent_comment=parent_comment,
                                                      **kwargs)
        inline_comment.full_clean()
        inline_comment.save()

    return inline_comment


def inline_comment_update(*, user: User, inline_comment: InlineComment):
    if inline_comment.has_children or not (user == inline_comment.author) or inline_comment.frozen:
        raise PermissionDenied('You cannot modify this comment')
    inline_comment = model_update(instance=inline_comment)
    return inline_comment


def inline_comment_delete(*, user: User,
                          inline_comment: InlineComment,
                          modified_article_contents: Iterable = None):
    if not (user == comment.author or user.is_staff):
        raise PermissionDenied("Action not allowed")
    # if no parent_comment and not has_children: validate sent article body if proper;
    # joint text nodes with common formatting that were once split due to thread_
    with transaction.atomic():
        inline_comment.delete()
