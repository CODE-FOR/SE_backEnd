from django.http import HttpRequest
from django.views.decorators.http import require_POST, require_GET, require_http_methods
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.utils import timezone
from django.core import serializers


from core.api.auth import jwt_auth
from core.api.utils import (ErrorCode, failed_api_response, parse_data,
                            response_wrapper, success_api_response,wrapped_api)

from core.models import Project, User, Topic, Discussion


@jwt_auth()
@require_POST
@response_wrapper
def create_topic(request: HttpRequest):
    """
    [method]: POST
    [path]: /topic/create
    """
    user = request.user
    data = parse_data(request)
    title = data.get('title')
    pid = data.get('project_id')
    if title is None or pid is None:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, "BAD ARGS.")
    try:
        project = Project.objects.get(id = pid)
    except ObjectDoesNotExist:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, "BAD project id.")
    topic = Topic(created_by=user, title=title, project=project)
    topic.save()
    return success_api_response({'id': topic.id})

@jwt_auth()
@require_POST
@response_wrapper
def update_topic(request: HttpRequest, id: int):
    """
    [method]: POST
    
    [path]: /topic/<id: int>
    """
    data = parse_data(request)
    title = data.get('title')
    top = data.get('top')
    try:
        topic = Topic.objects.get(id=id)
    except ObjectDoesNotExist:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, "ID NOT EXIST.")
    if topic.created_by != request.user and topic.project.create_user != request.user:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, "BAD USER.")
    if title is not None:
        topic.title = title
    if top is not None:
        if request.user != topic.project.create_user:
            return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, "UNPERMITTED USER.")
        topic.top = top
    topic.save()
    return success_api_response({})

@jwt_auth()
@require_GET
@response_wrapper
def get_topic(request: HttpRequest, id: int):
    """
    [method]: GET
    
    [path]: /topic/<id: int>
    """
    try:
        topic = Topic.objects.get(id=id)
    except ObjectDoesNotExist:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, "ID NOT EXIST.")
    return success_api_response(topic.to_dict())

@jwt_auth()
@require_http_methods('DELETE')
@response_wrapper
def delete_topic(request: HttpRequest, id: int):
    try:
        topic = Topic.objects.get(id=id)
    except ObjectDoesNotExist:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, "ID NOT EXIST.")
    if topic.created_by != request.user and topic.project.create_user != request.user:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, "BAD USER.")
    topic.delete()
    return success_api_response({})

@jwt_auth()
@require_GET
@response_wrapper
def get_topic_list(request: HttpRequest):
    """
    get comment
    
    [method]: GET
    
    [route]: /api/topic
    """
    data: dict = request.GET.dict()
    if data:
        user_id = data.get('user_id')
        keywords = data.get('keywords')
        project_id = data.get('project_id')
        pindex = data.get('pindex')
        psize = data.get('psize')
    else:
        user_id = None
        keywords = None
        project_id = None
        pindex = None
        psize = None
    if pindex is None:
        pindex = 1
    if psize is None:
        psize = 20
    query = Topic.objects.all()
    if user_id:
        query = query.filter(created_by__id = user_id)
    if project_id:
        query = query.filter(project__id = project_id)
    if keywords:
        for keyword in keywords:
            query = query.filter(title__icontains=keyword)
    query.order_by('-id')
    paginator = Paginator(query, psize)
    try:
        cp = paginator.page(pindex)
    except:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, "Bad page args.")
    re_data = {'topic_list': [topic.to_dict() for topic in cp.object_list], 'page_count': paginator.num_pages}
    return success_api_response(re_data)

TOPIC_API = wrapped_api({
    'POST': update_topic,
    'GET': get_topic,
    'DELETE': delete_topic,
})