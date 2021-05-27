"""
chat
"""
from django.db import models
from django.contrib.auth import get_user_model
from .user import User

READ_STATE_CHIOCES = (
    (0, 'Not read'),
    (1, 'Read'),
)


class Chat(models.Model):
    message = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='send_chat')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receive_chat')
    # read_state = models.IntegerField(choices=READ_STATE_CHIOCES)


class Chat_list(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='my_chat_list')
    target = models.ForeignKey(User, on_delete=models.CASCADE)
    update_time = models.DateTimeField(auto_now=True)
    unread = models.IntegerField(default=0)
    last_message = models.CharField(max_length=200, default='')

    def to_hash(self):
        rst = dict()
        rst.update({
            'id': self.target.id,
            'name': self.target.username,
            'email': self.target.email,
            'last_message': self.last_message,
            'have_unread_message': self.unread == 0,
            'unread_message_num': 2,
        })
        return rst

    def chat_in(self):
        self.save()

    def add_chat(self):
        self.unread += 1
        self.save()

    def clear_unread(self):
        self.unread = 0
        self.save()


def get_chat_list_by_id(user):
    lists = Chat_list.objects.filter(owner=user).order_by('-update_time')
    rst = dict()
    chat_list = []
    id_list = []
    for chat in lists:
        chat_list.append(chat.to_hash())
        id_list.append(chat.target.id)
    rst.update({
        'chat_user_list': chat_list,
        'id_list': id_list,
    })
    return rst


def add_chat_list_or_update_it(user, target):
    if Chat_list.objects.filter(owner=user, target=target).exists():
        Chat_list.objects.filter(owner=user, target=target).first().chat_in()
        return

    c = Chat_list
    c.target = target
    c.owner = user
    c.save()
