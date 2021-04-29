"""micro evidence
"""
from django.db import models
from .micro_knowledge import MicroKnowledge, MICRO_EVIDENCE
from .paper import Paper
from .user import User


class Interpretation(models.Model):
    """interpretation

    Fields:
        - 
    """

    paper = models.ForeignKey(Paper, on_delete=models.CASCADE, related_name='related_interpretation')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='create_paper')
    title = models.CharField(max_length=100)

    content = models.CharField(max_length=4096)

    is_deleted = models.BooleanField(default=False)
    is_up = models.BooleanField(default=False)

    def to_hash(self):
        rst = dict()
        rst.update({
            "id": self.id,
            "created_by": self.created_by.to_hash(),
            "content": self.content,
            "title": self.title,
            "paper": self.paper.to_hash(),
            "is_deleted": self.is_deleted,
            "created_at": self.created_at,
        })
        return rst

    def to_hash_for_paper(self):
        rst = dict()
        rst.update({
            "id": self.id,
            "created_by": self.created_by.to_hash(),
            "content": self.content,
            "title": self.title,
            "paper": self.paper_id,
            "created_at": self.created_at,
        })
        return rst