from django.db import models
from .tag import Tag
from .user import User


def search_by_keyword_and_tags(cls, tags, keyword):
    """
    search all the objects has keywords and tags
    :param cls: class of this method
    :param tags: list of topic id
    :param keyword: search title including this
    :return: a query set
    """
    items = cls.objects.all()
    for tag in tags:
        items = items & cls.objects.filter(tag_list__id__contains=tag)

    return (items & cls.objects.filter(title__contains=keyword)).distinct()
