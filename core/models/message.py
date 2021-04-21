"""
message
"""
from django.db import models
from django.contrib.auth import get_user_model
from .user import User

READ_STATE_CHIOCES = (
    (0, 'Not read'),
    (1, 'Read'),
)


class Message(models.Model):
    contend = models.CharField(max_length=200)
    aim_user = models.ForeignKey(User, on_delete=models.CASCADE)
    read_state = models.IntegerField(choices=READ_STATE_CHIOCES)
