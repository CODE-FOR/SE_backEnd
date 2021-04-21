from django.db import models
from core.models.user import User
from core.models.micro_knowledge import MicroKnowledge

UNREAD = 0
READ = 1

READ_STATUS_CHOICES = (
    (UNREAD, 'unread'),
    (READ, 'readed'),
)

MICRO_KNOWLEDGE_FAVOR = 1
MICRO_KNOWLEDGE_LIKE = 2
USER_FOLLOW = 3
JUDGE_FAIL_REASON = 4

CODE_CHOICE = (
    (MICRO_KNOWLEDGE_FAVOR, "micro knowledge has been favored."),
    (MICRO_KNOWLEDGE_LIKE, "micro knowledge has been like."),
    (USER_FOLLOW, "user has been follow."),
    (JUDGE_FAIL_REASON, "micro knowledge has been judged failed."),
)


class Notification(models.Model):
    """ notification

    Fields:
        - content: notification content
        - read_status: status of notification
    """
    created_at = models.DateTimeField(auto_now_add=True)

    content = models.CharField(max_length=1000)
    read_status = models.IntegerField(choices=READ_STATUS_CHOICES)
    code = models.IntegerField(choices=CODE_CHOICE)

    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='to_user')
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='from_user')
    micro_knowledge = models.ForeignKey(MicroKnowledge, on_delete=models.CASCADE, blank=True, null=True)

    def to_hash(self):
        rst = dict()
        rst.update({
            'created_at': self.created_at,
            'from_user': self.from_user.pk,
            'to_user': self.to_user.pk,
            'content': self.content,
            'code': self.code,
        })
        if self.micro_knowledge is not None:
            rst.update({
                'micro_knowledge': self.micro_knowledge.pk
            })
        return rst

    def has_read(self):
        self.read_status = READ
        self.save()

    @classmethod
    def new_notification(cls, code: int, from_user: User, to_user: User, content: str, micro_knowledge=None):
        try:
            new_notification = Notification(code=code,
                                            content=content,
                                            from_user=from_user,
                                            to_user=to_user,
                                            read_status=UNREAD)
            if micro_knowledge is not None:
                new_notification.micro_knowledge = micro_knowledge
            new_notification.save()
            return True
        except Exception:
            return False
