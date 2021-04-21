"""micro knowledge
"""
from django.db import models
from .tag import Tag
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


class MicroKnowledge(models.Model):
    """micro knowledge

    Fields:
        - created_at: created time
        - created_by: A foreignkey to user
        - like_list: a like list to this micro knowledge
        - comment_list: a comment list to this micro knowledge
        - tag_list: a tag list to this micro knowledge
        - content: summary of micro knowledge
        - judge_status: a micro knowledge is passed or not
        - pass_rating: users who rate pass
        - unpass_rating: users who rate unpass
    """
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_by')
    like_list = models.ManyToManyField(User, blank=True, related_name='like_list')
    # comment_list = models.ManyToManyField(User, through='Comment', related_name='comment_list')
    tag_list = models.ManyToManyField(to=Tag, related_name='tag_to_mk')
    content = models.CharField(max_length=1000)
    judge_status = models.IntegerField(choices=JUDGE_STATUS_CHIOCES)

    pass_voter = models.ManyToManyField(to=User, related_name='pass_voter')
    unpass_voter = models.ManyToManyField(to=User, related_name='unpass_voter')

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
