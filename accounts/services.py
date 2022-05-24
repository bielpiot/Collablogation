from .models import User
from ..articles.models import Article


def grant_beta_access(*, article: Article, granter: User, grantee: User) -> None:
    pass


def send_access_request(*, article: Article, sender: User, receiver: User) -> None:
    pass
