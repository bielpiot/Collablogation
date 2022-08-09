from accounts.auth_decorators import article_status_or_permission_required, article_status_and_permission_required
from accounts.perm_constants import view_permission, add_inline_comments_permission
from articles.models import Article
from common.utils import get_object, inline_serializer
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator as md
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from .models import Comment, InlineComment
from .selectors import comments_list_by_thread, inline_comment_list_by_thread, inline_comment_detail, comment_detail
from .services import (comment_create, comment_update, comment_delete,
                       inline_comment_create, inline_comment_delete, inline_comment_update)


class CommentListAPI(APIView):
    class OutputSerializer(serializers.ListSerializer):
        child = inline_serializer(fields={
            'id': serializers.UUIDField(),
            'author': serializers.PrimaryKeyRelatedField(read_only=True),
            'contents': serializers.CharField(),
            'thread_id': serializers.UUIDField()
        })

    @md(article_status_or_permission_required(permission=view_permission, status=(Article.PUBLISHED,)))
    def get(self, request, article_slug, **kwargs):
        article = get_object_or_404(Article, slug=article_slug)
        threads = comments_list_by_thread(article=article)
        data = self.OutputSerializer(threads, many=True).data
        return Response(data=data, status=HTTP_200_OK)


class CommentDetailAPI(APIView):
    class OutputSerializer(serializers.ModelSerializer):
        class Meta:
            model = Comment
            fields = ['id', 'author', 'contents', 'created', 'updated', 'parent_comment']

    @md(article_status_or_permission_required(permission=view_permission, status=Article.PUBLISHED))
    def get(self, request, comment_uid, article_slug, **kwargs):
        comment = get_object_or_404(Comment, uid=comment_uid, article__slug=article_slug)
        comment_detailed = comment_detail(user=request.user, comment=comment)
        serialized = self.OutputSerializer(comment_detailed)
        return Response(data=serialized.data, status=HTTP_200_OK)


class CommentCreateAPI(APIView):
    class InputSerializer(serializers.ModelSerializer):
        class Meta:
            model = Comment
            fields = ['contents']

    @md(article_status_and_permission_required(status=(Article.PUBLISHED,)))
    def post(self, request, article_slug, comment_uid=None, **kwargs):
        article = get_object_or_404(Article, slug=article_slug)
        serializer = self.InputSerializer(data=request.data)
        if serializer.is_valid():
            parent_comment = None
            if comment_uid:
                parent_comment = get_object(Comment, uid=comment_uid)
            comment_create(user=request.user, article=article,
                           parent_comment=parent_comment, **serializer.validated_data)
            return Response(status=HTTP_201_CREATED)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class CommentUpdateAPI(APIView):
    class InputSerializer(serializers.ModelSerializer):
        class Meta:
            model = Comment
            fields = ['contents']

    class OutPutSerializer(serializers.ModelSerializer):
        class Meta:
            model = Comment
            fields = ['id', 'author', 'contents', 'created', 'updated', 'parent_comment']

    @md(article_status_or_permission_required(status=(Article.PUBLISHED,)))
    def patch(self, request, comment_uid, article_slug, **kwargs):
        article = get_object_or_404(Article, slug=article_slug)
        comment = get_object_or_404(Comment, uid=comment_uid, article=article)
        input_serializer = self.InputSerializer(data=request.data)
        if input_serializer.is_valid():
            updated_comment = comment_update(user=request.user, comment=comment,
                                             data=input_serializer.validated_data, article=article)
            output_serializer = self.OutPutSerializer(updated_comment)
            return Response(status=HTTP_200_OK, data=output_serializer.data)
        return Response(input_serializer.errors, status=HTTP_400_BAD_REQUEST)


class CommentDeleteAPI(APIView):

    @md(article_status_or_permission_required(status=(Article.PUBLISHED,)))
    def delete(self, request, comment_uid, article_slug, **kwargs):
        article = get_object_or_404(Article, slug=article_slug)
        comment = get_object_or_404(Comment, uid=comment_uid, article__slug=article_slug)
        comment_delete(user=request.user, comment=comment, article=article)
        message = f"Comment has been successfully deleted"
        return Response({'message': message}, status=HTTP_204_NO_CONTENT)


class InlineCommentListAPI(APIView):
    class ThreadSerializer(serializers.ModelSerializer):
        pass

    class OutputSerializer(serializers.Serializer):
        pass

    @md(article_status_or_permission_required(permission=view_permission))
    def get(self, request, article_slug, **kwargs):
        article = get_object_or_404(Article, slug=article_slug)
        comments = inline_comment_list_by_thread(article=article)
        data = self.OutputSerializer(comments, many=True).data
        return Response(data=data)


class InlineCommentUpdateAPI(APIView):
    class InputSerializer(serializers.ModelSerializer):
        class Meta:
            model = InlineComment
            fields = ['contents']

    class OutputSerializer(serializers.ModelSerializer):
        class Meta:
            model = InlineComment
            fields = ['id', 'author', 'contents', 'created', 'thread_id']

    def patch(self, request, inline_comment_id, **kwargs):
        inline_comment = get_object_or_404(InlineComment, id=inline_comment_id)
        serialized_in = self.InputSerializer(data=request.data)
        updated_comment = inline_comment_update(user=request.user, data=serialized_in.validated_data)
        serialized_out = self.OutputSerializer(updated_comment)
        return Response(status=HTTP_200_OK, data=serialized_out.data)


class InlineCommentDetailAPI(APIView):
    class OutputSerializer(serializers.ModelSerializer):
        class Meta:
            model = InlineComment
            fields = ['author', 'contents', 'id']

    @md(article_status_and_permission_required(permission=view_permission, status=(Article.BETA, Article.DRAFT)))
    def get(self, request, article_slug, inline_comment_uid, **kwargs):
        article = get_object_or_404(Article, slug=article_slug)
        inline_comment_in = get_object_or_404(InlineComment, uid=inline_comment_uid)
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
    def post(self, request, article_slug, inline_comment_uid=None, **kwargs):
        article = get_object_or_404(Article, slug=article_slug)
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid()
        parent_comment = None
        if inline_comment_uid:
            parent_comment = get_object_or_404(InlineComment, uid=inline_comment_uid)
        inline_comment_create(user=request.user, article_id=article.id,
                              parent_comment=parent_comment, **serializer.validated_data)
        return Response(status=HTTP_201_CREATED)


class InlineCommentDeleteAPI(APIView):

    def delete(self, request, inline_comment_uid, **kwargs):
        inline_comment = get_object_or_404(InlineComment, uid=inline_comment_uid)
        inline_comment_delete(user=request.user, inline_comment=inline_comment)
        return Response(status=HTTP_204_NO_CONTENT)
