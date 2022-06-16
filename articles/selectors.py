from django.contrib.auth import get_user_model
from django.db.models.query import QuerySet
from django.core.exceptions import PermissionDenied
from django_filters import FilterSet

from .models import Article
from .perm_constants import view_permission

User = get_user_model()

art_view_suffix, _ = view_permission


class ArticleFilter(FilterSet):
    class Meta:
        model = Article
        fields = ('category', 'author')


def article_list(*, fetched_by: User, filters=None, status: Article.status = 'draft') -> QuerySet[Article]:
    filters = filters or {}
    query_match = {
        'draft': Article.drafts.filter(author=fetched_by),
        'archived': Article.archived.filter(author=fetched_by),
        'published': Article.published.all(),
        'beta': Article.beta.all(),
    }

    qs = query_match.get(status, Article.object.none())
    return ArticleFilter(filters, qs).qs


def article_detail(*, fetched_by: User, slug: str) -> Article:
    article = Article.objects.get(slug=slug)
    view_perm = article.id + art_view_suffix
    if not (article.status == 'published' or request.user.has_article_perm(view_perm)):
        raise PermissionDenied()
    # TODO depending on status, include comments or inline comments !
    return article
