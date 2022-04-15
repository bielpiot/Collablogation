from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.views import APIView

from .models import Article

User = get_user_model()


class PublishedArticlesList(APIView):
    class OutPutSerializer(serializers.ModelSerializer):
        class Meta:
            model = Article
