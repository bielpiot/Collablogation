from accounts.auth_decorators import article_status_or_permission_required, article_status_and_permission_required
from accounts.perm_constants import full_edit_permission, view_permission, delete_permission
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator as md
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.status import (HTTP_201_CREATED, HTTP_200_OK,
                                   HTTP_400_BAD_REQUEST, HTTP_204_NO_CONTENT)
from rest_framework.views import APIView
from taggit.serializers import (TagListSerializerField,
                                TaggitSerializer)

from .models import Article
from .selectors import article_list, article_detail
from .services import article_create, article_update, article_delete

User = get_user_model()


class ArticleCreateAPI(APIView):
    class InputSerializer(serializers.ModelSerializer, TaggitSerializer):
        class Meta:
            model = Article
            fields = ['title', 'contents', 'tags']
            optional_fields = ['category', ]

    def post(self, request, **kwargs):
        serializer = self.InputSerializer(data=request.data)
        if serializer.is_valid():
            article_create(user=request.user, **serializer.validated_data)
            return Response(data=serializer.data, status=HTTP_201_CREATED)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class ArticleUpdateAPI(APIView):
    class InputSerializer(serializers.ModelSerializer, TaggitSerializer):
        class Meta:
            model = Article
            fields = ['title', 'category', 'contents']

    @md(article_status_and_permission_required(permission=full_edit_permission,
                                               status=(Article.DRAFT, Article.BETA)))
    def patch(self, request, article_slug, **kwargs):
        article = get_object_or_404(Article, slug=article_slug)
        serializer = self.InputSerializer(data=request.data)
        if serializer.is_valid():
            serialized = self.InputSerializer(data=request.data)
            article_update(article=article, data=serialized.validated_data)
            return Response(status=HTTP_200_OK)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class ArticleListAPI(APIView):
    class OutputSerializer(serializers.ModelSerializer, TaggitSerializer):
        tags = TagListSerializerField()
        author = serializers.CharField(source='author.username')

        class Meta:
            model = Article
            fields = ['slug', 'title', 'author', 'category', 'tags']

    class FilterSerializer(serializers.Serializer):
        category = serializers.CharField(required=False)
        author = serializers.CharField(required=False)

    def get(self, request, status, **kwargs):
        filters = self.FilterSerializer(data=request.query_params)
        filters.is_valid(raise_exception=True)
        articles = article_list(user=request.user,
                                status=status,
                                filters=filters.validated_data)
        data = self.OutputSerializer(articles, many=True).data
        return Response(data, status=HTTP_200_OK)


class ArticleDetailAPI(APIView):
    class OutputSerializer(serializers.ModelSerializer, TaggitSerializer):
        tags = TaggitSerializer()

        class Meta:
            model = Article
            fields = ['id', 'author', 'title', 'slug', 'created', 'updated',
                      'publish_date', 'category', 'contents', 'status', 'tags']

    @md(article_status_or_permission_required(permission=view_permission, status=(Article.PUBLISHED,)))
    def get(self, request, article_slug, **kwargs):
        article = article_detail(user=request.user, slug=article_slug)
        data = self.OutputSerializer(article).data
        return Response(data, status=HTTP_200_OK)


class ArticleDeleteAPI(APIView):

    @md(article_status_and_permission_required(permission=delete_permission, status=(Article.DRAFT,
                                                                                     Article.BETA,
                                                                                     Article.ARCHIVED)))
    def delete(self, request, article_slug, **kwargs):
        article = get_object_or_404(Article, slug=article_slug)
        article_delete(article=article, user=request.user)
        message = f"Article {slug} has been successfully deleted"
        return Response({'message': message}, status=HTTP_204_NO_CONTENT)
