from django.http import HttpRequest
from django.views.decorators.http import require_POST, require_GET, require_http_methods
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.utils import timezone
from django.core import serializers
from datetime import datetime


from core.api.auth import jwt_auth
from core.api.utils import (ErrorCode, failed_api_response, parse_data,
                            response_wrapper, success_api_response,wrapped_api)

from core.models import Project, ProjectMicroKnowledge, User, Discussion, Timeline


@jwt_auth()
@require_POST
@response_wrapper
def create_project(request: HttpRequest):
    """
    [method]: POST
    [path]: /project/create
    """
    user = request.user
    data = parse_data(request)
    name = data.get('name')
    content = data.get('content')
    html_content = data.get('html_content')
    timeline_list = data.get('timeline_list')
    if name is None or content is None or html_content is None:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, "BAD ARGS.")
    project = Project(create_user=user, name=name, content=content, html_content=html_content)
    project.save()
    if timeline_list:
        for timeline_dict in timeline_list:
            time_string = timeline_dict.get('time')
            event = timeline_dict.get('event')
            if time_string is None or event is None:
                return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, "BAD ARGS.")
            time = datetime.strptime(time_string, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
            timeline = Timeline(time=time, event=event, project=project)
            timeline.save()
    return success_api_response({'id': project.id})

@jwt_auth()
@require_POST
@response_wrapper
def update_project(request: HttpRequest, id: int):
    """
    [method]: POST
    
    [path]: /project/<id: int>
    """
    data = parse_data(request)
    name = data.get('name')
    content = data.get('content')
    html_content = data.get('html_content')
    timeline_list = data.get('timeline_list')
    try:
        project = Project.objects.get(id=id)
    except ObjectDoesNotExist:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, "ID NOT EXIST.")
    if project.create_user != request.user:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, "BAD USER.")
    if name is not None:
        project.name = name
    if content is not None:
        project.content = content
    if html_content is not None:
        project.html_content = html_content
    project.save()
    if timeline_list:
        timelines=[]
        for timeline_dict in timeline_list:
            time_string = timeline_dict.get('time')
            event = timeline_dict.get('event')
            if time_string is None or event is None:
                return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, "BAD ARGS.")
            time = datetime.strptime(time_string, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
            print(time)
            timelines.append(Timeline(time=time, event=event, project=project))
        project.timeline_list.all().delete()
        for timeline in timelines:
            timeline.save()
    return success_api_response({})

@jwt_auth()
@require_GET
@response_wrapper
def get_project(request: HttpRequest, id: int):
    """
    [method]: GET
    
    [path]: /project/<id: int>
    """
    try:
        project = Project.objects.get(id=id)
    except ObjectDoesNotExist:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, "ID NOT EXIST.")
    return success_api_response(project.to_dict())

@jwt_auth()
@require_http_methods('DELETE')
@response_wrapper
def delete_project(request: HttpRequest, id: int):
    try:
        project = Project.objects.get(id=id)
    except ObjectDoesNotExist:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, "ID NOT EXIST.")
    if project.create_user != request.user:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, "BAD USER.")
    project.delete()
    return success_api_response({})

@jwt_auth()
@require_GET
@response_wrapper
def get_project_list(request: HttpRequest):
    """
    get comment
    
    [method]: GET
    
    [route]: /api/project
    
    parms:
		- pindex: int 
        - psize: int
    """
    data: dict = request.GET.dict()
    if data:
        user_id = data.get('user_id')
        keywords = data.get('keywords')
        pindex = data.get('pindex')
        psize = data.get('psize')
    else:
        user_id = None
        keywords = None
        pindex = None
        psize = None
    if pindex is None:
        pindex = 1
    if psize is None:
        psize = 20
    query = Project.objects.all()
    if user_id:
        query = query.filter(create_user__id = user_id)
    if keywords:
        for keyword in keywords:
            query = query.filter(content__icontains=keyword)
    query.order_by('-id')
    paginator = Paginator(query, psize)
    try:
        cp = paginator.page(pindex)
    except:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, "Bad page args.")
    re_data = {'project_list': [project.to_dict() for project in cp.object_list], 'page_count': paginator.num_pages}
    return success_api_response(re_data)

PROJECT_API = wrapped_api({
    'POST': update_project,
    'GET': get_project,
    'DELETE': delete_project,
})