from django.contrib.auth import get_user_model
from django.db.models.query import QuerySet
from django_filters import FilterSet

from Collablogation.accounts.perm_constants import view_permission
from .models import Article

User = get_user_model()

art_view_suffix, _ = view_permission


class ArticleFilter(FilterSet):
    class Meta:
        model = Article
        fields = ('category', 'author')


def article_list(*, user: User, filters=None, status: Article.status) -> QuerySet[Article]:
    filters = filters or {}
    query_match = {
        'draft': Article.drafts.filter(author=user) if user.is_authenticated else Article.objects.none(),
        'archived': Article.archived.filter(author=user) if user.is_authenticated else Article.objects.none(),
        'published': Article.published.all(),
        'beta': Article.beta.all(),
    }

    qs = query_match.get(status, Article.objects.none())

    return ArticleFilter(filters, qs).qs


def article_detail(*, user: User, slug: str) -> Article:
    article = get_object(Article, slug=slug)
    # TODO depending on status, include comments or inline comments !
    return article
