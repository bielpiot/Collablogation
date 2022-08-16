from typing import TypeVar

from django.db import models

# source: Hacksoftware Django Styleguide
DjangoModelType = TypeVar('DjangoModelType', bound=models.Model)
