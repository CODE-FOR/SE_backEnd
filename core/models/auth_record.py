"""auth record
"""
from django.db import models
from .user import User

# Create your models here
class AuthRecord(models.Model):
    """This model describes a user auth record
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    login_at = models.DateTimeField()
    expires_by = models.DateTimeField()
