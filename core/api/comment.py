import time

from django.http import HttpRequest
from django.views.decorators.http import require_POST, require_GET
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.utils import timezone
from django.core import serializers

from core.api.auth import jwt_auth
from core.api.utils import (ErrorCode, failed_api_response, parse_data,
                            response_wrapper, success_api_response)

from core.models import Comment, User
from core.models.interpretation import Interpretation


@jwt_auth()
@require_POST
@response_wrapper
def create_comment(request: HttpRequest):
    """
    create comment

    [method]: POST

    [route]: /api/comment/create
    params:
        - micro_knowledge_id: int
        - content: string
        - to_user_id: int
        - parent_comment_id: int
    """
    data: dict = parse_data(request)
    if not data:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, "Invalid request args.")

    user: User = request.user

    limits = Comment.objects.filter(user=user).order_by('-created_at')
    if limits.count() >= 20:
        limit_time = limits[19].created_at.timestamp()
        now_time = time.time()
        if now_time - limit_time <= 3600:
            return failed_api_response(ErrorCode.LIMIT, "reach post limit in an hour")

    knowledge_id = data.get('micro_knowledge_id')
    content = data.get('content')
    tu_id = data.get('to_user_id')
    pc_id = data.get('parent_comment_id')
    if knowledge_id is None or content is None:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, "Bad Key in Request.")
    if len(content) > 500:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, "Content size too large.")
    try:
        knowledge = Interpretation.objects.get(pk=knowledge_id)
    except ObjectDoesNotExist:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, "Bad Knowledge ID.")
    if tu_id is None:
        tu = None
    else:
        try:
            tu = User.objects.get(id=tu_id)
        except ObjectDoesNotExist:
            return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, "Bad User ID.")

    if pc_id is None:
        pc = None
    else:
        try:
            pc = knowledge.comment_list.get(id=pc_id)
        except ObjectDoesNotExist:
            return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, "Bad Comment ID.")
    # if (pc is None)^(tu is None):
    #    return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, "Bad parent Comment and to User.")
    comment = Comment(interpretation=knowledge, user=user, text=content,
                      to_user=tu, parent_comment=pc)
    comment.save()
    ret_data = {'id': comment.id}
    return success_api_response(ret_data)


@jwt_auth()
@require_POST
@response_wrapper
def delete_comment(request: HttpRequest):
    """
    delete comment
    
    [method]: POST
    
    [route]: /api/comment/delete
    
    parms:
		- id: int
    """
    data: dict = parse_data(request)
    if not data:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, "Invalid request args.")
    user: User = request.user
    comment_id = data.get('id')
    try:
        comment = Comment.objects.get(id=comment_id)
    except ObjectDoesNotExist:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, "Bad Knowledge ID.")
    if comment.user.id != user.id:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, "Wrong user ID")
    comment.safe_delete()
    return success_api_response({'id': comment_id})


@jwt_auth()
@require_GET
@response_wrapper
def get_comment(request: HttpRequest, id: int):
    """
    get comment
    
    [method]: GET
    
    [route]: /api/comment/:id
    
    parms:
		- id: int
    """
    comment_id = id
    try:
        comment = Comment.objects.get(id=comment_id)
    except ObjectDoesNotExist:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, "Bad Comment ID.")
    if comment.is_delete:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, "Bad Comment ID.")
    ret_data = comment.to_hash()
    return success_api_response(ret_data)


@jwt_auth()
@require_GET
@response_wrapper
def get_comment_list(request: HttpRequest):
    """
    get comment
    
    [method]: GET
    
    [route]: /api/comment
    
    parms:
        - micro_knowledge_id: int
		- pindex: int 
        - psize: int
    """
    data: dict = request.GET.dict()
    if not data:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, "Invalid request args.")
    else:
        mk_id = data.get('micro_knowledge_id')
        pindex = data.get('pindex')
        psize = data.get('psize')
    if mk_id is None:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, "Invalid request args.")
    if pindex is None:
        pindex = 1
    if psize is None:
        psize = 20000
    try:
        mk = Interpretation.objects.get(pk=mk_id)
    except ObjectDoesNotExist:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, "Invalid micro knowledge id.")
    paginator = Paginator(mk.comment_list.all(), psize)
    try:
        cp = paginator.page(pindex)
    except:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, "Bad page args.")

    comment_list = []
    for comment in cp.object_list:
        comment_list.append(comment.to_hash())

    re_data = {'comment_list': comment_list, 'page_count': paginator.num_pages}
    return success_api_response(re_data)
    # cl = list(cp.object_list.values())
    # return success_api_response({'comment_list': cl, 'page_count': paginator.count})
