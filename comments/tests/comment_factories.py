import factory
from ..models import Comment, InlineComment
from faker import Faker
from Collablogation.articles.tests.articles_factories import ArticleFactory
from Collablogation.accounts.tests.accounts_factories import UserFactory

faker = Faker()


class CommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Comment

    article = factory.SubFactory(ArticleFactory)
    author = factory.SubFactory(UserFactory)
    contents = factory.LazyAttribute(lambda _: faker.paragraph(nb=10))
    parent_comment = factory.SubFactory(CommentFactory, parent_comment=None)
