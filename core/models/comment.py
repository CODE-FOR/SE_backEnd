"""comment
"""
from django.db import models
from .user import User
from .interpretation import Interpretation


class Comment(models.Model):
    """comment

    Fields:
        - interpretation: a foreignkey to interpretation
        - user: a foreignkey to user
        - created_at = created time
        - text: comment content
    """
    interpretation = models.ForeignKey(Interpretation, on_delete=models.CASCADE, related_name="comment_list")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_comments")
    created_at = models.DateTimeField(auto_now_add=True)
    text = models.CharField(max_length=200)
    to_user = models.ForeignKey(User, on_delete=models.PROTECT, null=True, related_name="received_comments")
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, related_name="son_comment")
    is_delete = models.BooleanField(default=False)

    def to_hash(self):
        data: dict = {'id': self.id,
                      'username': self.user.username,
                      'user_id': self.user.id,
                      'created_at': self.created_at,
                      'text': self.text,
                      'micro_knowledge_id': self.interpretation.id,
                      }
        if self.to_user is not None:
            data['to_user'] = {'id': self.to_user.id, 'username': self.to_user.username}
        if self.parent_comment is not None:
            data['parent_comment_id'] = self.parent_comment.id
        return data

    def safe_delete(self):
        self.is_delete = True
        self.save()
