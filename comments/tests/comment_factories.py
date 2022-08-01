import factory
from accounts.tests.accounts_factories import UserFactory
from articles.tests.articles_factories import ArticleFactory
from comments.models import Comment, InlineComment
from faker import Faker

faker = Faker()


class CommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Comment
        django_get_or_create = ('article', 'author', 'parent_comment')

    article = factory.SubFactory(ArticleFactory)
    author = factory.SubFactory(UserFactory)
    contents = factory.LazyAttribute(lambda _: faker.paragraphs(nb=10))
    parent_comment = factory.LazyAttribute(lambda _: CommentFactory(parent_comment=None))


class InlineCommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = InlineComment

    article = factory.SubFactory(ArticleFactory)
    author = factory.SubFactory(UserFactory)
    contents = factory.LazyAttribute(lambda _: faker.paragraphs(nb=5))
    parent_comment = factory.LazyAttribute(lambda _: InlineCommentFactory(parent_comment=None))
    # thread_id = parent_comment.id
