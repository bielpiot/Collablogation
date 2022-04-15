from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import Article

User = get_user_model()


def article_publish(*, article: Article) -> Article:
    """
    Service modifying Post instance before publishing:
    1. clear all <span> elements serving as hooks for inline comments
    """
    Article.status = 'published'
    Article.published = timezone.now()


def grant_beta_access(*, article: Article, granter: User, grantee: User) -> Article:
    pass
