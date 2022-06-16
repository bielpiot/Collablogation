from .models import Comment, InlineComment
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from .selectors import comment_list, comment_detail
from .services import comment_create
from ..articles.models import Article
from ..api.utils import get_object


class CommentListApi(APIView):
    class OutputSerializer(serializers.ModelSerializer):
        class Meta:
            model = Comment
            fields = ['id', 'author', 'contents', 'created', 'updated', 'parent_comment']

    def get(self, request, slug):
        article_id = Article.objects.get(slug=slug).pk
        comments = comment_list(user=request.user, article_id=article)
        data = self.OutputSerializer(comments, many=True).data
        return Response(data)


class CommentDetailApi(APIView):
    class OutputSerializer(serializers.ModelSerializer):
        class Meta:
            model = Comment
            fields = ['id', 'author', 'contents', 'created', 'updated', 'parent_coment']

    def get(self, request, comment_id):
        pass


class CommentCreateApi(APIView):
    class InputSerializer(serializers.ModelSerializer):
        class Meta:
            model = Comment
            fields = ['contents', 'parent_comment']

    def post(self, request, slug):
        article = get_object(Article, slug=slug)
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid()
        comment_create(user=request.user, article=article, **serializer.validated_data)
        return Response(status=HTTP_200_OK)


class CommentUpdateApi(APIView):
    class InputSerializer(serializers.ModelSerializer):
        class Meta:
            model = Comment
            fields = ['id', 'contents']

        def put(self, request):
            pass

        def patch(self, request):
            pass


class InlineCommentListApi(APIView):
    class OutputSerializer(serializers.Serializer):
        pass


class InlineCommentUpdateApi(APIView):
    class InputSerializer(serializers.Serializer):
        pass


class InlineCommentDetailApi(APIView):
    class OutputSerializer(serializers.Serializer):
        pass

    def get(self, request):
        pass


class InlineCommentCreateApi(APIView):
    class InputSerializer(serializers.Serializer):
        pass

    def post(self, request):
        pass
