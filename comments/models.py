import uuid

from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from articles.models import Article


class BaseComment(models.Model):
    article = models.ForeignKey(Article, related_name='%(class)ss', on_delete=models.CASCADE, editable=False)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    contents = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    parent_comment = models.ForeignKey('self', related_name='replies', related_query_name='reply',
                                       null=True, on_delete=models.CASCADE)

    class Meta:
        abstract = True

    def clean(self):
        pass

    @property
    def has_children(self):
        return self._meta.model.objects.filter(parent_comment=self).exists()


class Comment(BaseComment):

    def __str__(self):
        return f'{self.author} comment on {self.post}'


class InlineComment(BaseComment):

    def __str__(self):
        return f'{self.author} beta comment on {self.post}'

    def clean(self):
        super().clean()
