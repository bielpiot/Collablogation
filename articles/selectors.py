from django.contrib.auth import get_user_model
from django.db.models.query import QuerySet

from .models import Article

User = get_user_model()


def draft_list(user: User) -> QuerySet[Article]:
    pass


def article_list(*, fetched_by: User, status: str, filters: None) -> QuerySet[Article]:
    filters = filters or {}
    post_ids = draft_list(user=fetched_by)
    return Article.objects.all()


def article_detail(*, fetched_by=User, article: Article):
    pass
