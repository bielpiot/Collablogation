from accounts import urls as acc_urls
from articles.apis import ArticleListApi, ArticleDetailApi, ArticleCreateAPI, ArticleUpdateApi, ArticleDeleteApi
from comments.apis import CommentListApi, CommentDetailApi, CommentCreateApi, CommentUpdateApi, CommentDeleteApi
from django.urls import include, path

comment_patterns = [
    path('', CommentListApi.as_view(), name='list'),
    path('create/', CommentCreateApi.as_view(), name='create'),
    path('<str:comment_uid>/', CommentDetailApi.as_view(), name='detail'),
    path('<str:comment_uid>/modify/', CommentUpdateApi.as_view(), name='update'),
    path('<str:comment_uid>/delete/', CommentDeleteApi.as_view(), name='delete'),
    path('<str:comment_uid>/reply/', CommentCreateApi.as_view(), name='reply')
]

article_patterns = [
    path('', ArticleListApi.as_view(), name='list'),
    path('<slug:article_slug>', ArticleDetailApi.as_view(), name='detail'),
    path('<slug:article_slug>/modify/', ArticleUpdateApi.as_view(), name='update'),
    path('<slug:article_slug>/delete/', ArticleDeleteApi.as_view(), name='delete'),
    path('<slug:article_slug>/comments/', include((comment_patterns, 'comments'), namespace='comments'))

]

urlpatterns = [
    path('create/', ArticleCreateAPI.as_view(), name='create'),
    path('user/', include(acc_urls)),
    path('main/', include((article_patterns, 'articles'), namespace='main'), {'status': 'published'}),
    path('beta/', include((article_patterns, 'articles'), namespace='beta'), {'status': 'beta'}),
    path('drafts/', include((article_patterns, 'articles'), namespace='drafts'), {'status': 'draft'}),
    path('archived/', include((article_patterns, 'articles'), namespace='archived'), {'status': 'archived'}),
]
