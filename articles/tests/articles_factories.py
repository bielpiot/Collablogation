import random

import factory
from accounts.tests.accounts_factories import UserFactory
from faker import Faker

from ..models import Article

faker = Faker()


def get_random_status():
    rd_choices = [x[0] for x in Article.READINESS_CHOICES]
    return random.choice(rd_choices)


class ArticleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Article
        # django_get_or_create = ('author',)

    author = factory.SubFactory(UserFactory)
    title = factory.LazyAttribute(lambda _: faker.text(max_nb_chars=50))
    category = factory.LazyAttribute(lambda _: faker.word())
    contents = factory.LazyAttribute(lambda _: faker.paragraphs(nb=10))
    status = factory.LazyFunction(get_random_status)
