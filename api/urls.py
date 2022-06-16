from ..articles.apis import ArticleListApi, ArticleDetailApi, ArticleCreateAPI, ArticleChangeApi
from ..comments.apis import CommentListApi, CommentDetailApi, CommentCreateApi, CommentUpdateApi
from django.urls import include, path

comment_patterns = [
    path('', CommentListApi.as_view()),
    path('create/', CommentCreateApi.as_view()),
    path('<uuid:id>/', CommentDetailApi.as_view()),
    path('<uuid:id>/modify/', CommentChangeApi.as_view()),
    path('<uuid:id>/delete/', CommentDeleteApi.as_view())
]

article_patterns = [
    path('', ArticleListApi.as_view()),
    path('<slug:slug>', ArticleDetailApi.as_view()),
    path('<slug:slug>/modify/', ArticleChangeApi.as_view()),
    path('<slug:slug>/delete/', ArticleDeleteApi.as_view()),
    path('comments/', include(comment_patterns))

]

urlpatterns = [
    path('create/', ArticleCreateAPI.as_view()),
    path('main/', include(article_patterns), {'status': 'published'}),
    path('beta/', include(article_patterns), {'status': 'beta'}),
    path('drafts/', include(article_patterns), {'status': 'draft'}),
    path('archived/', include(article_patterns), {'status': 'archived'}),
]
