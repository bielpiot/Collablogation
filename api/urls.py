from accounts import urls as acc_urls
from articles.apis import ArticleDetailAPI, ArticleCreateAPI, ArticleUpdateAPI, ArticleDeleteAPI, ArticleListAPI
from comments.apis import CommentDetailAPI, CommentCreateAPI, CommentUpdateAPI, CommentDeleteAPI, CommentListAPI
from django.urls import include, path

comment_patterns = [
    path('', CommentListAPI.as_view(), name='list'),
    path('create/', CommentCreateAPI.as_view(), name='create'),
    path('<str:comment_uid>/', CommentDetailAPI.as_view(), name='detail'),
    path('<str:comment_uid>/modify/', CommentUpdateAPI.as_view(), name='update'),
    path('<str:comment_uid>/delete/', CommentDeleteAPI.as_view(), name='delete'),
    path('<str:comment_uid>/reply/', CommentCreateAPI.as_view(), name='reply')
]

article_patterns = [
    path('', ArticleListAPI.as_view(), name='list'),
    path('<slug:article_slug>/', ArticleDetailAPI.as_view(), name='detail'),
    path('<slug:article_slug>/modify/', ArticleUpdateAPI.as_view(), name='update'),
    path('<slug:article_slug>/delete/', ArticleDeleteAPI.as_view(), name='delete'),
    path('<slug:article_slug>/comments/', include((comment_patterns, 'comments'), namespace='comments'))

]

urlpatterns = [
    path('', include(acc_urls)),
    path('create/', ArticleCreateAPI.as_view(), name='create'),
    path('main/', include((article_patterns, 'articles'), namespace='main'), {'status': 'published'}),
    path('beta/', include((article_patterns, 'articles'), namespace='beta'), {'status': 'beta'}),
    path('drafts/', include((article_patterns, 'articles'), namespace='drafts'), {'status': 'draft'}),
    path('archived/', include((article_patterns, 'articles'), namespace='archived'), {'status': 'archived'}),
]
