from django.views.decorators.http import require_http_methods
from django.http import HttpRequest

from .utils import (failed_api_response, ErrorCode,
                    success_api_response,
                    wrapped_api, response_wrapper)
import json

from core.models.tag import Tag, TAG, KEYWORD
from core.models.user import User

from core.api.auth import jwt_auth
from django.core.paginator import Paginator
from core.models.chat import Chat_list, Chat, get_chat_list_by_id, add_chat_list_or_update_it, get_one_message_by_id, get_all_message_by_id


# chat curd


@response_wrapper
@jwt_auth()
@require_http_methods('POST')
def get_user_chat_by_id(request: HttpRequest):
    """
    :param request:

    :return:
    """
    params = json.loads(request.body.decode())
    user = request.user

    target = params.get("user_id")
    target = User.objects.filter(id=target).first()

    rst = target.to_hash_chat()

    return success_api_response(rst)


@response_wrapper
@jwt_auth()
@require_http_methods('POST')
def clear_unread_by_id(request: HttpRequest):
    """
    :param request:

    :return:
    """
    params = json.loads(request.body.decode())
    user = request.user

    target = params.get("user_id")
    target = User.objects.filter(id=target).first()
    if Chat_list.objects.filter(owner=user, target=target).exists():
        Chat_list.objects.filter(owner=user, target=target).first().clear_unread()

    return success_api_response({})


@response_wrapper
@jwt_auth()
@require_http_methods('GET')
def get_chat_list(request: HttpRequest):
    """ get micro evidence information
    :return:
    """
    p = request.user
    rst = get_chat_list_by_id(p)

    return success_api_response(rst)


@response_wrapper
@jwt_auth()
@require_http_methods('POST')
def add_user_into_list(request: HttpRequest):
    params = json.loads(request.body.decode())
    user = request.user

    target = params.get("user_id")
    target = User.objects.filter(id=target).first()

    add_chat_list_or_update_it(user, target)
    return success_api_response({})


@response_wrapper
@jwt_auth()
@require_http_methods('GET')
def get_message_list_by_id(request: HttpRequest):
    p = request.user

    return success_api_response({
        'message_list': get_all_message_by_id(p)
    })


@response_wrapper
@jwt_auth()
@require_http_methods('POST')
def get_message_by_id(request: HttpRequest):
    params = json.loads(request.body.decode())
    user = request.user

    target = params.get("user_id")
    target = User.objects.filter(id=target).first()

    return success_api_response({
        'message_list': get_one_message_by_id(user, target)
    })


def add_chat_message(sender, receiver, msg):
    sender = User.objects.filter(id=sender).first()
    receiver = User.objects.filter(id=receiver).first()
    c = Chat()
    c.receiver = receiver
    c.sender = sender
    c.message = msg
    c.save()
    Chat_list.objects.filter(owner=sender, target=receiver).first().update_msg(msg)
    if sender != receiver:
        cl = Chat_list.objects.filter(owner=receiver, target=sender)
        if cl.exists():
            cl = cl.first()
            cl.add_chat()
            cl.update_msg(msg)
    return c.created_at


