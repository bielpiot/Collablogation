from accounts.auth_decorators import article_status_or_permission_required, article_status_and_permission_required
from articles.models import Article
from articles.perm_constants import view_permission, add_inline_comments_permission
from common.utils import get_object, inline_serializer
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Comment
from .selectors import comment_list, comment_detail
from .services import comment_create


class CommentListApi(APIView):
    class OutputSerializer(serializers.ListSerializer):
        comments = inline_serializer(many=True, fields={
            'id': serializers.UUIDField(),
            'author': serializers.PrimaryKeyRelatedField(read_only=True),
            'contents': serializers.CharField(),
        })

    class FilterSerializer(serializers.Serializer):
        category = serializers.CharField(required=False)
        author = serializers.CharField(required=False)

    def get(self, request, slug):
        article = get_object(Article, slug=slug)
        filters = self.FilterSerializer(data=request.query_params)
        filters.is_valid(raise_exception=True)
        comments = comment_list(user=request.user,
                                article=article,
                                filters=filters.validated_data)
        data = self.OutputSerializer(comments, many=True).data
        return Response(data)


class CommentDetailApi(APIView):
    class OutputSerializer(serializers.ModelSerializer):
        class Meta:
            model = Comment
            fields = ['id', 'author', 'contents', 'created', 'updated', 'parent_coment']

    @article_status_or_permission_required(permission=view_permission, status=Article.PUBLISHED)
    def get(self, request, comment_uid):
        comment = get_object(Comment, uid=comment_uid)
        comment_ = comment_detail(user=request.user, comment=comment)
        serialized = self.OutputSerializer(comment_)
        return Response(serialized.data)


class CommentCreateApi(APIView):
    class InputSerializer(serializers.ModelSerializer):
        class Meta:
            model = Comment
            fields = ['contents', 'parent_comment']

    @article_status_or_permission_required(permission=view_permission, status=(Article.PUBLISHED,))
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


class CommentDeleteApi(APIView):
    class InputSErializer(serializers.ModelSerializer):
        class Meta:
            model = Comment
            fields = ['id']

    def delete(self, request):
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

    @article_status_and_permission_required(permission=add_inline_comments_permission,
                                            status=(Article.BETA, Article.DRAFT))
    def post(self, request):
        pass
