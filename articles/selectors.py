from django.contrib.auth import get_user_model
from django.db.models.query import QuerySet

from .models import Article

User = get_user_model()


def draft_list(*, fetched_by: User, filters=None) -> QuerySet[Article]:
    filters = filters or {}
    return Article.drafts.filter(author=User)


def article_list(*, fetched_by: User, filters=None) -> QuerySet[Article]:
    filters = filters or {}
    return Article.published.filter(filters)


def article_detail(*, fetched_by: User, id: str) -> Article:
    pass
