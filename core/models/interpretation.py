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

    source = models.CharField(max_length=300)

    is_deleted = models.BooleanField(default=False)
    is_up = models.BooleanField(default=False)

    def to_hash(self):
        rst = dict()
        rst.update({
            "id": self.id,
            "created_by": self.created_by.to_hash()
            "paper": self.paper.to_hash(),
            "is_deleted": self.is_deleted,
            "source": self.source,
            "created_at": self.created_at,
            "type": self.micro_type(),
        })
        return rst
