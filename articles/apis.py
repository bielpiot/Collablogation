from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.views import APIView

from .models import Article

User = get_user_model()


class ArticleCreateAPI(APIView):
    class InputSerializer(serializers.Serializer):
        title = serializers.CharField()
        category = serializers.CharField()
        contents = serializers.TextField()
        status = serializers.CharField()

    def post(self):
        pass


class ArticleChangeApi(APIView):
    class InputSerializer(serializers.Serializer):
        pass

    def put(self):
        pass

    def patch(self):
        pass


class ArticleListApi(APIView):
    class OutputSerializer(serializers.Serializer):
        id = serializers.UUIDField()

    def get(self):
        pass


class ArticleDetailApi(APIView):
    class OutputSerializer(serializers.Serializer):
        id = serializers.UUIDField()

    def get(self):
        pass
