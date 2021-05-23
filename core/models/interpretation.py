"""micro evidence
"""
from django.db import models
from .micro_knowledge import MicroKnowledge, MICRO_EVIDENCE
from .paper import Paper
from .user import User
from .tag import Tag


class Interpretation(models.Model):
    """interpretation

    Fields:
        - 
    """

    paper = models.ForeignKey(Paper, on_delete=models.CASCADE, related_name='related_interpretation')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='create_interpretation')
    title = models.CharField(max_length=100)
    content = models.CharField(max_length=4096)
    tag_list = models.ManyToManyField(to=Tag, related_name='tag_to_interpretation')

    is_deleted = models.BooleanField(default=False)
    is_up = models.BooleanField(default=False)

    like_list = models.ManyToManyField(to='User', related_name='like_interpretation')
    collect_list = models.ManyToManyField(to='User', related_name='collect_interpretation')

    def be_liked(self, user):
        if self.like_list.filter(id=user.id):
            self.like_list.remove(user)
        else:
            self.like_list.add(user)

    def be_collected(self, user):
        if self.collect_list.filter(id=user.id):
            self.collect_list.remove(user)
        else:
            self.collect_list.add(user)

    def like_num(self):
        return self.like_list.count()

    def collect_num(self):
        return self.collect_list.count()

    def is_like(self, user):
        return self.like_list.filter(id=user).exists()

    def is_collect(self, user):
        return self.collect_list.filter(id=user).exists()

    def to_hash(self, user):
        if hasattr(user, 'id'):
            user = user.id
        rst = dict()
        tags = list(self.tag_list.values('id', 'name', 'type'))  # dic
        rst.update({
            "type": 1,
            "tags": tags,
            "id": self.id,
            "created_by": self.created_by.to_hash(),
            "content": self.content,
            "title": self.title,
            "paper": self.paper.to_hash(user),
            "created_at": self.created_at,
            "like_num": self.like_num(),
            "collect_num": self.collect_num(),
            "is_like": self.is_like(user),
            "is_collect": self.is_collect(user),
        })
        return rst

    def to_hash_for_paper(self, user):
        if hasattr(user, 'id'):
            user = user.id
        rst = dict()
        tags = list(self.tag_list.values('id', 'name', 'type'))
        rst.update({
            "type": 1,
            "tags": tags,
            "id": self.id,
            "created_by": self.created_by.to_hash(),
            "content": self.content,
            "title": self.title,
            "paper": self.paper_id,
            "created_at": self.created_at,
            "like_num": self.like_num(),
            "collect_num": self.collect_num(),
            "is_like": self.is_like(user),
            "is_collect": self.is_collect(user),
        })
        return rst


# 按置顶+时间倒序获取paper
def get_interpretation_ordered():
    interpretations = Interpretation.objects.all().order_by('-created_at')
    return interpretations
