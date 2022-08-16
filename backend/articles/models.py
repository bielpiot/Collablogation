import uuid

from django.conf import settings
from django.core.exceptions import FieldError
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from taggit.managers import TaggableManager
from taggit.models import GenericUUIDTaggedItemBase, TaggedItemBase


class PublishedManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset().filter(status=Article.PUBLISHED)


class DraftsManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset().filter(status=Article.DRAFT)


class BetaManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset().filter(status=Article.BETA)


class ArchivedManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset().filter(status=Article.ARCHIVED)


class UUIDTaggedItem(GenericUUIDTaggedItemBase, TaggedItemBase):
    # If you only inherit GenericUUIDTaggedItemBase, you need to define
    # a tag field. e.g.
    # tag = models.ForeignKey(Tag, related_name="uuid_tagged_items", on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")


class Article(models.Model):
    """
    Model dedicated to store blog posts data
    """
    DRAFT = 'draft'
    BETA = 'beta'
    PUBLISHED = 'published'
    ARCHIVED = 'archived'

    READINESS_CHOICES = [
        (DRAFT, 'Draft'),
        (BETA, 'Beta'),
        (PUBLISHED, 'Published'),
        (ARCHIVED, 'Archived')
    ]

    id = models.UUIDField(primary_key=True, db_index=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='posts', on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=27)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    publish_date = models.DateTimeField(blank=True, null=True)
    category = models.CharField(max_length=25, default='misc')
    contents = models.TextField()
    status = models.CharField(max_length=15, choices=READINESS_CHOICES, default='draft')

    tags = TaggableManager(through=UUIDTaggedItem)

    objects = models.Manager()
    published = PublishedManager()
    beta = BetaManager()
    drafts = DraftsManager()
    archived = ArchivedManager()

    def __str__(self):
        return self.title

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
        if not self.slug or 'title' in kwargs.get('update_fields', []):
            self.slug = self._create_unique_slug()
        super().save(*args, **kwargs)
