from django.http import HttpRequest
from django.views.decorators.http import require_POST, require_GET, require_http_methods
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.utils import timezone
from django.core import serializers


from core.api.auth import jwt_auth
from core.api.utils import (ErrorCode, failed_api_response, parse_data,
                            response_wrapper, success_api_response, wrapped_api)

from core.models import Project, ProjectMicroKnowledge, User, MicroKnowledge


@jwt_auth()
@require_POST
@response_wrapper
def create_project_mk(request: HttpRequest):
    """
    [method]: POST
    [path]: /project/micro-knowledge
    """
    user = request.user
    data = parse_data(request)
    pid = data.get('project_id')
    mkid = data.get('microknowledge_id')
    reason = data.get('reason')
    if pid is None or mkid is None or reason is None:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, "BAD ARGS.")
    try:
        project = Project.objects.get(id=pid)
        mk = MicroKnowledge.objects.get(id=mkid)
    except ObjectDoesNotExist:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, "ID NOT EXIST.")
    pmk = ProjectMicroKnowledge(create_user=user, project=project, micro_knowledge=mk,reason=reason)
    pmk.save()
    return success_api_response({'id': pmk.id})


@jwt_auth()
@require_POST
@response_wrapper
def update_project_mk(request: HttpRequest, id: int):
    """
    [method]: POST

    [path]: /project/micro-knowledge/<id: int>
    """
    data = parse_data(request)
    reason = data.get('reason')
    try:
        pmk = ProjectMicroKnowledge.objects.get(id=id)
    except ObjectDoesNotExist:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, "ID NOT EXIST.")
    if pmk.create_user != request.user:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, "BAD USER.")
    if reason is not None:
        pmk.reason = reason
    pmk.save()
    return success_api_response({})


@jwt_auth()
@require_GET
@response_wrapper
def get_project_mk(request: HttpRequest, id: int):
    """
    [method]: GET

    [path]: /project/micro-knowledge/<id: int>
    """
    try:
        pmk = ProjectMicroKnowledge.objects.get(id=id)
    except ObjectDoesNotExist:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, "ID NOT EXIST.")
    return success_api_response(pmk.to_dict())


@jwt_auth()
@require_http_methods('DELETE')
@response_wrapper
def delete_project_mk(request: HttpRequest, id: int):
    try:
        pmk = ProjectMicroKnowledge.objects.get(id=id)
    except ObjectDoesNotExist:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, "ID NOT EXIST.")
    if pmk.create_user != request.user and pmk.project.create_user != request.user:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, "BAD USER.")
    pmk.delete()
    return success_api_response({})


@jwt_auth()
@require_GET
@response_wrapper
def get_project_mk_list(request: HttpRequest):
    """
    get comment

    [method]: GET

    [route]: /api/project/micro-knowledge

    parms:
                - pindex: int 
        - psize: int
    """
    data: dict = request.GET.dict()
    if data:
        project_id = data.get('project_id')
        pindex = data.get('pindex')
        psize = data.get('psize')
    else:
        project_id = None
        pindex = None
        psize = None
    if pindex is None:
        pindex = 1
    if psize is None:
        psize = 20
    query = ProjectMicroKnowledge.objects.all()
    if project_id is None:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, 'BAD ARGS.')
    query = query.filter(project__id=project_id)
    query = query.order_by('-id')
    paginator = Paginator(query, psize)
    try:
        cp = paginator.page(pindex)
    except:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, "Bad page args.")
    re_data = {'project_mk_list': [pmk.to_dict(
    ) for pmk in cp.object_list], 'page_count': paginator.num_pages}
    return success_api_response(re_data)


PROJECT_MK_API = wrapped_api({
    'POST': update_project_mk,
    'GET': get_project_mk,
    'DELETE': delete_project_mk,
})
