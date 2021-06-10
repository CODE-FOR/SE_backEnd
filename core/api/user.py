import json

from django.views.decorators.http import require_http_methods
from django.http import HttpRequest
from django.core.paginator import Paginator
from .utils import (failed_api_response, ErrorCode,
                    success_api_response,
                    wrapped_api, response_wrapper)
from core.api.auth import jwt_auth
from core.models.micro_evidence import MicroEvidence
from core.models.micro_conjecture import MicroConjecture
from core.models.notification import (Notification, USER_FOLLOW)
from core.models.user import User, Ban


# follow apis


@response_wrapper
@jwt_auth()
@require_http_methods('POST')
def follow(request: HttpRequest, pid: int):
    """ follow someone
    :param request: http request
    :param pid: follow user id
    :return:
    """
    user = request.user
    _success = user.follow_by_id(pid)

    Notification.new_notification(
        code=USER_FOLLOW,
        from_user=user,
        to_user=User.objects.get(pk=pid),
        content="Congratulation! you have a new fan")

    if _success:
        return success_api_response({})
    else:
        return failed_api_response({})


@response_wrapper
@jwt_auth()
@require_http_methods('POST')
def unfollow(request: HttpRequest, pid: int):
    """ follow someone
    :param request: http request
    :param pid: follow user id
    :return:
    """
    user = request.user
    _success = user.unfollow_by_id(pid)
    if _success:
        return success_api_response({})
    else:
        return failed_api_response({})


@response_wrapper
@jwt_auth()
@require_http_methods('GET')
def list_follower_recent(request: HttpRequest, pindex: int):
    """ get favor list
    :param request:
        num_per_page: num_per_page
        micro_evidence: boolean, get micro evidence
        micro_conjecture: boolean, get micro conjecture
    :param pindex: which page
    :return:
    """

    # some api will be used in method
    def getTime(elem):
        from datetime import datetime
        created_at_time = elem.get('created_at', None)
        if created_at_time and created_at_time.__class__ == datetime:
            return created_at_time
        else:
            return datetime.now()

    # basic params
    params = request.GET.dict()
    num_per_page = 20
    if params.get('num_per_page', None):
        num_per_page = int(params.get('num_per_page', None))
    if num_per_page <= 0:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, "num_per_page should be bigger than 0.")
    p = request.user
    followers = p.followers.all()
    # make list
    recent_list = []
    for follower in followers:
        if params.get('micro_evidence', None) == 'true':
            micro_evidence_list = MicroEvidence.objects.filter(created_by=follower, judge_status=1)
            for micro_evidence in micro_evidence_list:
                rst = micro_evidence.to_hash()
                rst.update({
                    "is_like": micro_evidence.is_like(p.id),
                    "is_favor": micro_evidence.is_favor(p.id),
                })
                recent_list.append(rst)
        if params.get('micro_conjecture', None) == 'true':
            micro_conjecture_list = MicroConjecture.objects.filter(created_by=follower, judge_status=1)
            for micro_conjecture in micro_conjecture_list:
                rst = micro_conjecture.to_hash()
                rst.update({
                    "is_like": micro_conjecture.is_like(p.id),
                    "is_favor": micro_conjecture.is_favor(p.id),
                })
                recent_list.append(rst)
    recent_list.sort(key=getTime, reverse=True)
    # paginate
    paginator = Paginator(recent_list, num_per_page)
    recent_page = paginator.page(pindex)
    return success_api_response({
        "page": list(recent_page),
        "has_next": recent_page.has_next(),
        "has_previous": recent_page.has_previous(),
        "number": recent_page.number,
        "page_num": paginator.num_pages,
    })


@response_wrapper
@jwt_auth()
@require_http_methods('GET')
def list_user_all(request: HttpRequest, pindex: int):
    params = request.GET.dict()
    num_per_page = 5

    if params.get('num_per_page', None):
        num_per_page = int(params.get('num_per_page', None))

    if num_per_page <= 0:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, "num_per_page should be bigger than 0.")

    users = User.objects.all()

    # paginate
    paginator = Paginator(users, num_per_page)
    recent_page = paginator.page(pindex)

    user_list = []
    for user in recent_page.object_list:
        user_list.append(user.to_hash_list())

    return success_api_response({
        "user_list": user_list,
        "has_next": recent_page.has_next(),
        "has_previous": recent_page.has_previous(),
        "cur_page": recent_page.number,
        "total_page": paginator.num_pages,
    })


@response_wrapper
@jwt_auth()
@require_http_methods('GET')
def list_ban_all(request: HttpRequest, pindex: int):
    params = request.GET.dict()
    num_per_page = 5

    if params.get('num_per_page', None):
        num_per_page = int(params.get('num_per_page', None))

    if num_per_page <= 0:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, "num_per_page should be bigger than 0.")

    users = Ban.objects.filter(valid=True)

    # paginate
    paginator = Paginator(users, num_per_page)
    recent_page = paginator.page(pindex)

    user_list = []
    for user in recent_page.object_list:
        user_list.append(user.to_hash())

    return success_api_response({
        "ban_list": user_list,
        "has_next": recent_page.has_next(),
        "has_previous": recent_page.has_previous(),
        "cur_page": recent_page.number,
        "total_page": paginator.num_pages,
    })


@response_wrapper
@jwt_auth()
@require_http_methods('POST')
def ban(request: HttpRequest):
    params = json.loads(request.body.decode())

    user = params.get("userId")
    reason = params.get("reason")

    _success = User.objects.get(id=user).ban(reason)

    if _success:
        return success_api_response({})
    else:
        return failed_api_response({})


@response_wrapper
@jwt_auth()
@require_http_methods('POST')
def unban(request: HttpRequest):
    params = json.loads(request.body.decode())

    user = params.get("userId")

    _success = User.objects.get(id=user).unban()

    return success_api_response({})
