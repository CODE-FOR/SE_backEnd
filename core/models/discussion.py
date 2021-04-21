from django.db import models
from .user import User

class Discussion(models.Model):
    topic = models.ForeignKey('Topic', on_delete=models.CASCADE, related_name="discussion_list")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sended_discussion")
    created_at = models.DateTimeField(auto_now_add=True)
    text = models.CharField(max_length=200)
    to_user = models.ForeignKey(User, on_delete=models.PROTECT, null = True, related_name="recived_discussion")
    parent_discussion = models.ForeignKey('Discussion', on_delete=models.CASCADE, null=True, related_name="son_discussion")
    
    def to_dict(self) -> dict:
        data: dict = {'id': self.id, 
            'username': self.user.username, 
            'user_id': self.user.id, 
            'created_at': self.created_at, 
            'text': self.text, 
            'topic_id': self.topic.id,
            }
        if self.to_user is not None:
            data['to_user']=self.to_user.simple_to_dict()
        if self.parent_discussion is not None:
            data['parent_discussion_id']= self.parent_discussion.id
        return data
