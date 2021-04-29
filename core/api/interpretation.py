from django.views.decorators.http import require_http_methods
from django.http import HttpRequest

from .utils import (failed_api_response, ErrorCode,
                    success_api_response,
                    wrapped_api, response_wrapper)
import json

from core.models.tag import Tag, TAG, KEYWORD
from core.models.user import User

from core.api.auth import jwt_auth
from core.models.paper import Paper, get_up, get_by_id
from django.core.paginator import Paginator
from core.models.interpretation import Interpretation


# interpretation curd


@response_wrapper
@jwt_auth()
@require_http_methods('POST')
def create_interpretation(request: HttpRequest):
    """
    :param request:
        title: string
        content: string
        paper_id: int
        tags: list of tag | tag: {name, type}
    :return:
        interpretation_id
    """
    params = json.loads(request.body.decode())
    user = request.user
    if params.get('user_id'):
        user = User.objects.get(pk=params.get('user_id'))

    interpretation = Interpretation()
    interpretation.title = params.get("title")
    interpretation.content = params.get("content")
    paper = get_by_id(params.get("paper_id"))
    if paper is None:
        return failed_api_response(ErrorCode.ID_NOT_EXISTS, "paper id doesn't exist!")
    interpretation.paper = paper
    interpretation.created_by = user
    interpretation.save()

    for tag in params.get("tags"):
        tag_name = tag.get('name', None)
        tag_type = tag.get('type', None)
        if tag_name is None:
            return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, "tag params miss argument: tag_name.")
        if tag_type is None:
            return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, "tag params miss argument: tag_type.")
        if Tag.objects.filter(type=tag_type).filter(name=tag_name).exists():
            tag = Tag.objects.filter(type=tag_type).filter(name=tag_name).first()
        else:
            tag = Tag(name=tag_name, type=tag_type)
            tag.save()
        interpretation.tag_list.add(tag)

    return success_api_response({
        "id": interpretation.id
    })


@response_wrapper
@jwt_auth()
@require_http_methods('GET')
def get_interpretation_by_id(request: HttpRequest, id: int):
    """ get micro evidence information
    :param request:
    :param id: primary key
    :return:
    """
    p = request.user
    interpretation = Interpretation.objects.get(pk=id)
    rst = interpretation.to_hash()

    return success_api_response(rst)


INTERPRETATION_API = wrapped_api({
    # 'POST': create_paper,
    # 'DELETE': delete_paper,
    # 'PUT': update_micro_evidence,
    'GET': get_interpretation_by_id
})
