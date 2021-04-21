"""
User
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import validate_comma_separated_integer_list


class User(AbstractUser):
    """
    Field
        - nick_name: nick name
        - follow: follow user
        - favorate
        - is_confirmed: email is confirmed
    """
    nick_name = models.CharField(max_length=20)
    institution = models.CharField(max_length=20, blank=True, null=True)
    icon = models.ImageField(upload_to="images/%Y%m/%d/icons", default='images/default_user_icon.jpg')

    followers = models.ManyToManyField('User')
    favorites = models.ManyToManyField('MicroKnowledge', related_name='favorites')
    is_confirmed = models.BooleanField(default=False)
    is_sponsor = models.BooleanField(default=False, null=True)
    user_tags = models.CharField(validators=[validate_comma_separated_integer_list], max_length=70000,
                                    blank=True, null=True, default='')

    class Meta(AbstractUser.Meta):
        pass
    
    def simple_to_dict(self):
        return {
            'nick_name': self.nick_name,
            'id': self.id,
            'username': self.username,
        }

    def get_fan(self):
        """
        fan: 粉丝，关注user的人
        :return: 粉丝列表
        """
        return self.user_set.all()


    def get_follower(self):
        """
        follower: user关注的人
        :return: 关注的人列表
        """
        return self.followers.all()

    def follow_by_id(self, pid):
        """
        关注另外一个用户
        :param pid: 对方用户的id
        :return: 操作是否成功: boolean
        """
        try:
            p = User.objects.get(pk=pid)
            self.followers.add(p)
            return True
        except Exception:
            return False

    def unfollow_by_id(self, pid):
        """
        解除对另一个用户的关注
        :param pid: 对方用户的id
        :return: 操作是否成功: boolean
        """
        try:
            p = User.objects.get(pk=pid)
            self.followers.remove(p)
            return True
        except Exception:
            return False


class ConfirmString(models.Model):
    """confirm string
    Field
        - code: check code
        - user: user
    """
    code = models.CharField(max_length=5)
    email = models.CharField(max_length=50)

    def __str__(self):
        return self.email + ":   " + self.code
