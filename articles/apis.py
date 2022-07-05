from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from .models import Article
from .selectors import article_list, article_detail
from .services import article_create, article_edit
from Collablogation.common.utils import inline_serializer, get_object

User = get_user_model()


class ArticleCreateAPI(APIView):
    class InputSerializer(serializers.ModelSerializer):
        class Meta:
            model = Article
            fields = ['title', 'category', 'contents', 'status']

    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid()
        article_create(user=request.user, **serializer.validated_data)
        return Response(status=HTTP_200_OK)


class ArticleChangeApi(APIView):
    class InputSerializer(serializers.ModelSerializer):
        class Meta:
            model = Article
            fields = ['title', 'publish_date', 'category', 'contents', 'status']

    def patch(self, request, slug):
        article = get_object(Article, slug=slug)
        article_edit(article=article, user=request.user)


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
        articles = article_list(fetched_by=request.user,
                                status=status,
                                filters=filters.validated_data)
        data = self.OutputSerializer(articles, many=True).data
        return Response(data)


class ArticleDetailApi(APIView):
    class OutputSerializer(serializers.ModelSerializer):
        # comments = inline_serializer(many=True, fields={
        #     'id': serializers.UUIDField(),
        #     'author': serializers.PrimaryKeyRelatedField(),
        #     'contents': serializers.CharField(),
        #     'parent_comment': serializers.PrimaryKeyRelatedField()
        # })

        class Meta:
            model = Article
            fields = ['id', 'author', 'title', 'slug', 'created', 'updated',
                      'publish_date', 'category', 'contents', 'status']

    def get(self, request, slug):
        article = article_detail(fetched_by=request.user, slug=slug)
        data = self.OutputSerializer(article).data
        return Response(data)
