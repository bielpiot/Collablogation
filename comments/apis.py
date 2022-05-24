from .models import Comment, InlineComment
from rest_framework import serializers
from rest_framework.views import APIView


class InlineCommentsListApi(APIView):
    class OutputSerializer(serializers.Serializer):
        pass


class InlineCommentChangeApi(APIView):
    class InputSerializer(serializers.Serializer):
        pass


class InlineCommentDetail(APIView):
    class OutputSerializer(serializers.Serializer):
        pass

    def get(self, request):
        pass


class InlineCommentCreate(APIView):
    class InputSerializer(serializers.Serializer):
        pass

    def post(self, request):
        pass
