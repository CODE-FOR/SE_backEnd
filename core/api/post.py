from django.views.decorators.http import require_http_methods
from django.http import HttpRequest

from .utils import (failed_api_response, ErrorCode,
                    success_api_response,
                    wrapped_api, response_wrapper)
import json

from core.models.user import User
from core.api.auth import jwt_auth
from django.core.paginator import Paginator



@response_wrapper
@jwt_auth()
@require_http_methods('GET')
def follow_recent(request: HttpRequest, pindex):
    """
    get a page as order in time
    :param request:
        user_id: request user id
    :param pindex: page index
    :return:
    """
    p = request.user

    params = request.GET.dict()
    pindex = params.get('pindx')

    user_to = User.objects.filter(id=p.id).first()

    items = sorted(user_to.get_post_follow_unsorted(), key=lambda keys: keys['created_at'], reverse=True)
    total_count = len(items)

    num_per_page = 5
    if params.get('num_per_page', None):
        num_per_page = int(params.get('num_per_page', None))
    paginator = Paginator(items, num_per_page)
    result = paginator.page(pindex)
    return success_api_response({
        "page_num": paginator.num_pages,
        "recent": result,
    })


@response_wrapper
@jwt_auth()
@require_http_methods('GET')
def get_post_by_id(request: HttpRequest, uid):
    """
    get a page as order in time
    :param request:
        user_id: request user id
    :param pindex: page index
    :return:
    """
    p = request.user

    params = request.GET.dict()
    pindex = params.get('pindx')

    user_to = User

    if User.objects.filter(id=uid).exists():
        user_to = User.objects.filter(id=uid).first()
    else:
        failed_api_response(ErrorCode.ID_NOT_EXISTS, "user id not exists!")

    items = sorted(user_to.get_post_unsorted(), key=lambda keys: keys['created_at'], reverse=True)
    total_count = len(items)

    num_per_page = 5
    if params.get('num_per_page', None):
        num_per_page = int(params.get('num_per_page', None))
    paginator = Paginator(items, num_per_page)
    result = paginator.page(pindex)
    return success_api_response({
        "total_count": total_count,
        "posts": result,
    })


@response_wrapper
@jwt_auth()
@require_http_methods('GET')
def get_collect_by_id(request: HttpRequest, uid):
    """
    get a page as order in time
    :param request:
        user_id: request user id
    :param pindex: page index
    :return:
    """
    p = request.user

    params = request.GET.dict()
    pindex = params.get('pindx')

    user_to = User

    if User.objects.filter(id=uid).exists():
        user_to = User.objects.filter(id=uid).first()
    else:
        failed_api_response(ErrorCode.ID_NOT_EXISTS, "user id not exists!")

    items = sorted(user_to.get_collect_unsorted(), key=lambda keys: keys['created_at'], reverse=True)
    total_count = len(items)

    num_per_page = 5
    if params.get('num_per_page', None):
        num_per_page = int(params.get('num_per_page', None))
    paginator = Paginator(items, num_per_page)
    result = paginator.page(pindex)
    return success_api_response({
        "total_count": total_count,
        "posts": result,
    })
