import uuid
from django.conf import settings
# from django.contrib.auth import get_user_model
from django.core.exceptions import FieldError
from django.db import models
from django.utils.text import slugify
from taggit.managers import TaggableManager


# User = get_user_model()


class PublishedManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset().filter(status='published')


class DraftsManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset().filter(status='draft')


class BetaManager(models.Manager):
    def beta(self, *args, **kwargs):
        return super().get_queryset().filter(status='beta')


# Create your models here.
class Article(models.Model):
    """
    Model dedicated to store blog posts data
    """
    READINESS_CHOICES = [('draft', 'Draft'), ('beta', 'Beta'), ('published', 'Published')]

    uuid = models.UUIDField(primary_key=True, db_index=True, default=uuid.uuid4)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='posts', on_delete=models.PROTECT)
    title = models.CharField(max_length=50)
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=27)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    publish_date = models.DateTimeField(blank=True, null=True)
    category = models.CharField(max_length=25, default='misc')
    contents = models.TextField()
    status = models.CharField(max_length=15, choices=READINESS_CHOICES, default='draft')

    tags = TaggableManager()

    published = PublishedManager()
    beta = BetaManager()
    drafts = DraftsManager()

    def publish(self):
        pass

    def _create_unique_slug(self):
        max_length = self._meta.get_field('slug').max_length
        base_slug = slug = slugify(self.title)[:(max_length - 2)]
        count = 0
        while Article.objects.filter(slug__iexact=slug).exists():
            count += 1
            slug = f'{base_slug}-{count}'
            if count > 9:
                raise FieldError('Please provide different title')
        return slug

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._create_unique_slug()
        super().save(*args, **kwargs)
