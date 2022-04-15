import factory
from django.contrib.auth import get_user_model
from faker import Faker

from .. import signals
from ..models import Account

faker = Faker()
User = get_user_model()


@factory.django.mute_signals(signals.post_save)
class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ('username',)

    username = factory.LazyAttribute(lambda _: faker.name())
    email = factory.LazyAttribute(lambda _: faker.unique.email())


@factory.django.mute_signals(signals.post_save)
class AccountFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Account

    user = factory.SubFactory(UserFactory)
    about = factory.LazyAttribute(lambda _: faker.paragraph(nb=10))
    # contact =
    # followed =
    # favourite_posts = 
