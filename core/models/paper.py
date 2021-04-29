"""paper
"""
from django.db import models
from .tag import Tag
from .topic import Topic
from .user import User

FAILED = -1
JUDGING = 0
PASSED = 1

JUDGE_STATUS_CHIOCES = (
    (FAILED, 'Failed'),
    (JUDGING, 'Judging'),
    (PASSED, 'Passed'),
)

MICRO_KNOWLEDGE = 0
MICRO_EVIDENCE = 1
MICRO_CONJECTURE = 2


class Paper(models.Model):
    """paper

    Fields:
        - created_at: created time
        - created_by: A foreignkey to user
        - title: title of the paper
        - abstract: abstract of the paper
        - author: author of the paper
        - published_year: time when the paper published
        - topic_list: a topic list of the paper
        - tag_list: a tag list of the paper
        - paper_link: url of the paper
        - is_deleted: delete symbol
        - is_up: is up
    """
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='create_paper')
    title = models.CharField(max_length=100)
    abstract = models.CharField(max_length=4096)
    source = models.CharField(max_length=300)
    # authors
    published_year = models.IntegerField(default=2000)
    # topic_list = models.ManyToManyField(to=Topic, related_name='topic_to_paper')
    tag_list = models.ManyToManyField(to=Tag, related_name='tag_to_paper')
    is_deleted = models.BooleanField(default=False)
    is_up = models.BooleanField(default=False)

    def get_author(self):
        return self.authors.values_list('name')

    def add_author(self, authors):
        for author in authors:
            author_model = Paper_author()
            author_model.name = author
            author_model.paper = self
            author_model.save()

    def to_hash(self):
        rst = dict()
        tags = list(self.tag_list.values('id', 'name', 'type'))  # dic
        author = list(self.get_author())  # tuple
        rst.update({
            "id": self.pk,
            "created_by": {
                "id": self.created_by.id,
                "username": self.created_by.username,
            },
            "tags": tags,  # dic
            "abstract": self.abstract,
            "source": self.source,
            "published_year": self.published_year,
            "created_at": self.created_at,
            "author": author,  # tuple
            "title": self.title
        })
        return rst


def get_up():
    papers = Paper.objects.all().order_by('-is_up', '-created_at')
    '''
    if tags:
        for tag_str in tags:
            tag_list = Tag.objects.filter(name__icontains=tag_str)
            qs_tag = cls.objects.none()
            for tag in tag_list:
                qs_tag = qs_tag | cls.objects.filter(tag_list__id__contains=tag.id)
            qs = qs & qs_tag
    if keywords:
        for keyword in keywords:
            qs = qs & cls.objects.filter(content__icontains=keyword)
    '''
    return papers


'''
    def favorites_num(self):
        return self.favorites.values().count()

    def is_favor(self, pid):
        try:
            p = User.objects.get(pk=pid)
            return p.favorites.values().filter(pk=self.id).exists()
        except Exception:
            return False

    def like_num(self):
        return self.like_list.values().count()

    def is_like(self, pid):
        try:
            p = User.objects.get(pk=pid)
            return p.like_list.values().filter(pk=self.id).exists()
        except Exception:
            return False

    def micro_type(self):
        return MICRO_KNOWLEDGE

    @classmethod
    def search_by_keywords_and_tags(cls, keywords=None, tags=None):
        """
        search all the objects has keywords and tags
        :param keywords: iterator of string, search while in content
        :param tags: iterator of string, search the tags in content
        :return: a query set
        """
        tags = tags.split() if tags is not None else []
        keywords = keywords.split() if keywords is not None else []
        qs = cls.objects.all()
        if tags:
            for tag_str in tags:
                tag_list = Tag.objects.filter(name__icontains=tag_str)
                qs_tag = cls.objects.none()
                for tag in tag_list:
                    qs_tag = qs_tag | cls.objects.filter(tag_list__id__contains=tag.id)
                qs = qs & qs_tag
        if keywords:
            for keyword in keywords:
                qs = qs & cls.objects.filter(content__icontains=keyword)
        return qs.distinct()
'''


class Paper_author(models.Model):
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE, related_name='authors')
    name = models.CharField(max_length=50)
