import random

import factory
from faker import Faker

from ..models import Article
from ...accounts.tests.accounts_factories import UserFactory

faker = Faker()


def get_random_status():
    rd_choices = [x[0] for x in Article.READINESS_CHOICES]
    return random.choice(rd_choices)


class ArticleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Article

    author = factory.SubFactory(UserFactory)
    title = factory.LazyAttribute(lambda _: faker.title())
    category = factory.LazyAttribute(lambda _: faker.word())
    contents = factory.LazyAttribute(lambda _: faker.paragraph(nb=10))
    status = factory.LazyFunction(get_random_status)
