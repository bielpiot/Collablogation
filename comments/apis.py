from accounts.auth_decorators import article_status_or_permission_required, article_status_and_permission_required
from accounts.perm_constants import view_permission, add_inline_comments_permission
from articles.models import Article
from common.utils import get_object, inline_serializer
from django.utils.decorators import method_decorator as md
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT
from rest_framework.views import APIView

from .models import Comment, InlineComment
from .selectors import comments_list_by_thread, comment_detail, inline_comment_list_by_thread, inline_comment_detail
from .services import comment_create, comment_update, comment_delete, inline_comment_create, inline_comment_delete


class CommentListAPI(APIView):
    class OutputSerializer(serializers.ListSerializer):
        comments = inline_serializer(many=True, fields={
            'id': serializers.UUIDField(),
            'author': serializers.PrimaryKeyRelatedField(read_only=True),
            'contents': serializers.CharField(),
        })

    @md(article_status_or_permission_required(permission=view_permission, status=(Article.PUBLISHED,)))
    def get(self, request, article_slug):
        article = get_object(Article, slug=article_slug)
        comments = comments_list_by_thread(article=article)
        data = self.OutputSerializer(comments, many=True).data
        return Response(data=data)


class CommentDetailAPI(APIView):
    class OutputSerializer(serializers.ModelSerializer):
        class Meta:
            model = Comment
            fields = ['id', 'author', 'contents', 'created', 'updated', 'parent_comment']

    @md(article_status_or_permission_required(permission=view_permission, status=Article.PUBLISHED))
    def get(self, request, comment_uid, article_slug):
        article = get_object(Article, slug=article_slug)
        comment = get_object(Comment, uid=comment_uid, article=article)
        comment_ = comment_detail(user=request.user, comment=comment)
        serialized = self.OutputSerializer(comment_)
        return Response(data=serialized.data, status=HTTP_200_OK)


class CommentCreateApPI(APIView):
    class InputSerializer(serializers.ModelSerializer):
        class Meta:
            model = Comment
            fields = ['contents']

    @md(article_status_and_permission_required(status=(Article.PUBLISHED,)))
    def post(self, request, slug, comment_uid=None):
        article = get_object(Article, slug=slug)
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid()
        parent_comment = None
        if comment_uid:
            parent_comment = get_object(Comment, uid=comment_uid)
        comment_create(user=request.user, article=article,
                       parent_comment=parent_comment, **serializer.validated_data)
        return Response(status=HTTP_201_CREATED)


class CommentUpdateAPI(APIView):
    class InputSerializer(serializers.ModelSerializer):
        class Meta:
            model = Comment
            fields = ['contents']

    class OutPutSerializer(serializers.ModelSerializer):
        class Meta:
            model = Comment
            fields = ['id', 'author', 'contents', 'created', 'updated', 'parent_comment']

    def patch(self, request, comment_uid, article_slug):
        input_serializer = self.InputSerializer(data=request.data)
        article = get_object(Article, slug=article_slug)
        comment = get_object(Comment, uid=comment_uid, article=article)
        updated_comment = comment_update(user=request.user, comment=comment,
                                         data=input_serializer.validated_data, article=article)
        output_serializer = self.OutPutSerializer(updated_comment)
        return Response(status=HTTP_200_OK, data=output_serializer.data)


class CommentDeleteAPI(APIView):

    def delete(self, request, comment_uid, article_slug):
        article = get_object(Article, slug=article_slug)
        comment = get_object(Comment, uid=comment_uid, article=article)
        status = comment_delete(user=request.user, comment=comment)
        return Response(status=status)


class InlineCommentListAPI(APIView):
    class ThreadSerializer(serializers.ModelSerializer):
        pass

    class OutputSerializer(serializers.Serializer):
        pass

    @md(article_status_or_permission_required(permission=view_permission))
    def get(self, request, article_slug):
        article = get_object(Article, slug=article_slug)
        comments = inline_comment_list_by_thread(article=article)
        data = self.OutputSerializer(comments, many=True).data
        return Response(data=data)


class InlineCommentUpdateAPI(APIView):
    class InputSerializer(serializers.ModelSerializer):
        class Meta:
            model = InlineComment
            fields = ['contents']

    def patch(self, request, inline_comment_id):
        inline_comment = get_object(InlineComment, id=inline_comment_id)
        serialized = self.InputSerializer(data=request.data)
        updated_comment = inline_comment_update(user=request.user)


class InlineCommentDetailAPI(APIView):
    class OutputSerializer(serializers.ModelSerializer):
        class Meta:
            model = InlineComment
            fields = ['author', 'contents', 'id']

    @md(article_status_and_permission_required(permission=view_permission, status=(Article.BETA, Article.DRAFT)))
    def get(self, request, article_slug, inline_comment_uid):
        article = get_object(Article, slug=article_slug)
        inline_comment_in = get_object(InlineComment, uid=inline_comment_uid)
        inline_comment_out = inline_comment_detail(article=article, inline_comment=inline_comment_in)
        serialized = self.OutputSerializer(inline_comment_out)
        return Response(data=serialized.data, status=HTTP_200_OK)


class InlineCommentCreateAPI(APIView):
    class InputSerializer(serializers.ModelSerializer):
        class Meta:
            model = InlineComment
            fields = ['contents']

    @md(article_status_and_permission_required(permission=add_inline_comments_permission,
                                               status=(Article.BETA, Article.DRAFT)))
    def post(self, request, article_slug, inline_comment_uid=None):
        article = get_object(Article, slug=article_slug)
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid()
        parent_comment = None
        if inline_comment_uid:
            parent_comment = get_object(InlineComment, uid=inline_comment_uid)
        inline_comment_create(user=request.user, article_id=article.id,
                              parent_comment=parent_comment, **serializer.validated_data)
        return Response(status=HTTP_201_CREATED)


class InlineCommentDeleteAPI(APIView):

    def delete(self, request, inline_comment_uid):
        inline_comment = get_object(InlineComment, uid=inline_comment_uid)
        inline_comment_delete(user=request.user, inline_comment=inline_comment)
        return Response(status=HTTP_204_NO_CONTENT)
