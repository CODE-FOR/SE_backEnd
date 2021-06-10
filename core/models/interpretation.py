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
    delete_reason = models.CharField(default='', max_length=128)
    is_up = models.BooleanField(default=False)

    like_list = models.ManyToManyField(to='User', related_name='like_interpretation')
    collect_list = models.ManyToManyField(to='User', related_name='collect_interpretation')

    def safe_delete(self, reason):
        self.is_deleted = True
        self.delete_reason = reason
        self.save()
        # delete comment
        for comment in self.comment_list.all():
            comment.safe_delete()

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

    def be_reported(self, user, reason):
        new_report = Interpretation_report()
        new_report.reason = reason
        new_report.interpretation_id = self
        new_report.created_by = user
        new_report.save()
        return new_report.pk

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
    interpretations = Interpretation.objects.filter(is_deleted=False).order_by('-created_at')
    return interpretations


class Interpretation_report(models.Model):
    report_id = models.IntegerField(primary_key=True, auto_created=True)
    interpretation_id = models.ForeignKey(Interpretation, on_delete=models.CASCADE, related_name='reports')
    reason = models.CharField(max_length=512)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='report_interpretation')

    is_solved = models.BooleanField(default=False)

    def to_hash(self, user):
        rst = dict()
        rst.update({
            "id": self.pk,
            "created_by": self.created_by.to_hash(),
            "reason": self.reason,
            "created_at": self.created_at,
            "interpretation": self.interpretation_id.to_hash(user),
        })
        return rst

    def solve(self):
        self.is_solved = True
        self.save()


def get_all_interpretation_report():
    reports = Interpretation_report.objects.filter(interpretation_id__is_deleted=False, is_solved=False).order_by('-created_at')
    return reports
