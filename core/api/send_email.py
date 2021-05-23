# _*_ coding: utf-8 _*_
"""send email function
"""
# import datetime
import random
import string
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from core.models.user import ConfirmString, User


def make_confirm_string(email: str):
    """generate confirm string

    Arguments:
        user {User} -- user

    Returns:
        str -- confirm string
    """
    # now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    code = "".join(random.sample(string.ascii_letters + string.digits, 4))
    if ConfirmString.objects.filter(email=email).exists():
        confirm = ConfirmString.objects.get(email=email)
        confirm.code = code
        confirm.save()
    else:
        ConfirmString.objects.create(code=code, email=email)
    return code


def send_email(email, code):
    """send register email

    Arguments:
        email {str} -- email addr
        code {str} -- check code
    """

    subject = '来自造论子论文解读平台的注册邮件'

    text_content = '''感谢注册造论子论文解读平台，如果你看到这条消息，说明你的邮箱服务器不提供HTML链接功能，请联系管理员！'''

    template = loader.get_template('send_email.html')

    html_content = template.render(
        {
            'code': code
        }
    )

    msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


def send_forget(email, code):
    """send register email

    Arguments:
        email {str} -- email addr
        code {str} -- check code
    """

    subject = '来自造论子论文解读平台的修改密码确认邮件'

    text_content = '''感谢使用造论子论文解读平台，如果你看到这条消息，说明你的邮箱服务器不提供HTML链接功能，请联系管理员！'''

    template = loader.get_template('send_forget.html')

    html_content = template.render(
        {
            'name': User.objects.get(email=email).username,
            'code': code
        }
    )

    msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
