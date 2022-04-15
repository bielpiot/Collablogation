from django.contrib.auth import get_user_model

from .models import InlineComment
from ..posts.models import Post

User = get_user_model()


def inline_comment_create(*, user=User, post=Post, **kwargs) -> InlineComment:
    pass


def inline_comment_hook():
    pass
