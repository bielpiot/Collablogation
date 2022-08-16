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


class ArticleListAPI(APIView):
    """
    Endpoint returning list of all articles with given status.
    Drafts and archived list are filtered for request user being an author.
    GET request only.
    """

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
        return Response(data=data, status=HTTP_200_OK)


class ArticleDetailAPI(APIView):
    """
    Endpoint returning detailed article data. GET request only.
    """

    class OutputSerializer(serializers.ModelSerializer, TaggitSerializer):
        tags = TagListSerializerField()

        class Meta:
            model = Article
            fields = ['id', 'author', 'title', 'slug', 'created', 'updated',
                      'publish_date', 'category', 'contents', 'status', 'tags']

        # def __init__(self, *args, **kwargs):
        #     if self.fields['status'] != Article.PUBLISHED:
        #         self.fields['publish_date'].pop()
        #     super().__init__(self, *args, **kwargs)

        def to_representation(self, instance):
            if instance.status != Article.PUBLISHED:
                del self.fields['publish_date']
            return super().to_representation(instance)

    @md(article_status_or_permission_required(permission=view_permission, status=(Article.PUBLISHED,)))
    def get(self, request, article_slug, **kwargs):
        article = get_object_or_404(Article, slug=article_slug)
        article_detailed = article_detail(user=request.user, article=article)
        data = self.OutputSerializer(article_detailed).data
        return Response(data=data, status=HTTP_200_OK)


class ArticleCreateAPI(APIView):
    """
    Endpoint responsible for article creation. POST request accepted only.
    """

    class InputSerializer(serializers.ModelSerializer, TaggitSerializer):
        tags = TagListSerializerField()

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
    """
    Endpoint responsible for article instance update. PATCH request only.
    """

    class InputSerializer(serializers.ModelSerializer, TaggitSerializer):
        tags = TagListSerializerField()

        class Meta:
            model = Article
            fields = ['title', 'category', 'contents', 'tags']

    class OutputSerializer(serializers.ModelSerializer, TaggitSerializer):
        tags = TaggitSerializer()

        class Meta:
            model = Article
            fields = ['id', 'author', 'title', 'slug', 'created', 'updated',
                      'publish_date', 'category', 'contents', 'status', 'tags']

    @md(article_status_and_permission_required(permission=full_edit_permission,
                                               status=(Article.DRAFT, Article.BETA)))
    def patch(self, request, article_slug, **kwargs):
        article = get_object_or_404(Article, slug=article_slug)
        input_serializer = self.InputSerializer(data=request.data, partial=True)
        if input_serializer.is_valid():
            updated_article = article_update(article=article, data=input_serializer.validated_data)
            output_serializer = self.OutputSerializer(updated_article)
            return Response(data=output_serializer.data, status=HTTP_200_OK)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class ArticleDeleteAPI(APIView):
    """
    Endpoint responsible for article instance deletion. Accepted request: DELETE
    """

    @md(article_status_and_permission_required(permission=delete_permission, status=(Article.DRAFT,
                                                                                     Article.BETA,
                                                                                     Article.ARCHIVED)))
    def delete(self, request, article_slug, **kwargs):
        article = get_object_or_404(Article, slug=article_slug)
        article_delete(article=article, user=request.user)
        message = f"Article {article} has been successfully deleted"
        return Response({'message': message}, status=HTTP_204_NO_CONTENT)
