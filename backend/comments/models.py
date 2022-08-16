import uuid

from articles.models import Article
from django.conf import settings
from django.db import models
from django_extensions.db.fields import ShortUUIDField


class BaseComment(models.Model):
    article = models.ForeignKey(Article, related_name='%(class)ss', on_delete=models.CASCADE)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    uid = ShortUUIDField(unique=True, editable=False, null=True)
    contents = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    parent_comment = models.ForeignKey('self', related_name='replies', related_query_name='reply',
                                       null=True, blank=True, on_delete=models.CASCADE)
    frozen = models.BooleanField(default=False)
    thread_id = models.UUIDField(default=None, null=True, blank=True)

    class Meta:
        abstract = True

    @property
    def has_children(self):
        return self._meta.model.objects.filter(parent_comment=self).exists()

    def save(self, *args, **kwargs):
        if self.parent_comment is not None:
            self.thread_id = self.parent_comment.thread_id
        else:
            self.thread_id = self.id
        super().save(*args, **kwargs)


class Comment(BaseComment):

    def __str__(self):
        return f'{self.author} comment on {self.article}'


class InlineComment(BaseComment):

    def __str__(self):
        return f'{self.author} beta comment on {self.article}'
