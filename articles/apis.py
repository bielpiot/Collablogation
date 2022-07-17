from accounts.auth_decorators import article_status_or_permission_required, article_status_and_permission_required
from common.utils import get_object
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.status import (HTTP_201_CREATED, HTTP_200_OK,
                                   HTTP_400_BAD_REQUEST, HTTP_204_NO_CONTENT)
from rest_framework.views import APIView

from .models import Article
from .perm_constants import full_edit_permission, view_permission, delete_permission
from .selectors import article_list, article_detail
from .services import article_create, article_update, article_delete

User = get_user_model()


class ArticleCreateAPI(APIView):
    class InputSerializer(serializers.ModelSerializer):
        class Meta:
            model = Article
            fields = ['title', 'category', 'contents', 'status']

    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        if serializer.is_valid():
            article_create(user=request.user, **serializer.validated_data)
            return Response(serializer.data, status=HTTP_201_CREATED)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class ArticleUpdateApi(APIView):
    class InputSerializer(serializers.ModelSerializer):
        class Meta:
            model = Article
            fields = ['title', 'publish_date', 'category', 'contents']

    @article_status_and_permission_required(permission=full_edit_permission, status=(Article.DRAFT, Article.BETA))
    def patch(self, request, slug):
        article = get_object(Article, slug=slug)
        article_update(article=article, user=request.user)


class ArticleListApi(APIView):
    class OutputSerializer(serializers.ModelSerializer):
        class Meta:
            model = Article
            fields = ['id', 'title', 'author', 'category']

    class FilterSerializer(serializers.Serializer):
        category = serializers.CharField(required=False)
        author = serializers.CharField(required=False)

    def get(self, request, status):
        filters = self.FilterSerializer(data=request.query_params)
        filters.is_valid(raise_exception=True)
        articles = article_list(user=request.user,
                                status=status,
                                filters=filters.validated_data)
        data = self.OutputSerializer(articles, many=True).data
        return Response(data, status=HTTP_200_OK)


class ArticleDetailApi(APIView):
    class OutputSerializer(serializers.ModelSerializer):
        class Meta:
            model = Article
            fields = ['id', 'author', 'title', 'slug', 'created', 'updated',
                      'publish_date', 'category', 'contents', 'status']

    @article_status_or_permission_required(permission=view_permission, status=(Article.PUBLISHED,))
    def get(self, request, slug):
        article = article_detail(user=request.user, slug=slug)
        data = self.OutputSerializer(article).data
        return Response(data, status=HTTP_200_OK)


class ArticleDeleteApi(APIView):
    class InputSerializer(serializers.ModelSerializer):
        class Meta:
            model = Article
            fields = ['id', 'slug', 'author']

    @article_status_and_permission_required(permission=delete_permission, status=(Article.DRAFT,
                                                                                  Article.BETA,
                                                                                  Article.ARCHIVED))
    def delete(self, request, slug):
        article = get_object(Article, slug=slug)
        article_delete(article=article, user=request.user)
        message = f"Article {slug} has been successfully deleted"
        return Response({'message': message}, status=HTTP_204_NO_CONTENT)
