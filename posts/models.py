from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.
class Post(models.Model):
    """
    Model dedicated to store blog posts data
    """
    READINESS = [('draft', 'Draft'), ('beta', 'Beta'), ('published', 'Published')]

    author = models.ForeignKey(User, related_name='posts', on_delete=models.DO_NOTHING)
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    published = models.DateTimeField(blank=True, null=True)
    category = models.CharField(max_length=25, default='misc')
    contents = models.TextField()
    status = models.CharField(max_length=15, choices=READINESS, default='draft')




