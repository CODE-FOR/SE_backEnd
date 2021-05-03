from django.views.decorators.http import require_http_methods
from django.http import HttpRequest

from .utils import (failed_api_response, ErrorCode,
                    success_api_response,
                    wrapped_api, response_wrapper)
import json

from core.models.tag import Tag, TAG, KEYWORD
from core.models.user import User

from core.api.auth import jwt_auth
from core.models.paper import Paper, get_paper_ordered_dec, get_paper_by_id
from django.core.paginator import Paginator
from core.models.interpretation import Interpretation, get_interpretation_ordered


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
    paper = get_paper_by_id(params.get("paper_id"))
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


@response_wrapper
@jwt_auth()
@require_http_methods('GET')
def list_interpretation_page(request: HttpRequest, pindex):
    """
    get a page as order in time
    :param request:
        user_id: request user id
    :param pindex: page index
    :return:
    """
    params = dict(request.GET)

    interpretations = get_interpretation_ordered()
    interpretation_num = Interpretation.objects.count()
    p = request.user
    if params.get('user_id'):
        p = User.objects.get(pk=params.get('user_id'))
    num_per_page = 5
    if params.get('num_per_page', None):
        num_per_page = int(params.get('num_per_page', None))
    paginator = Paginator(interpretations, num_per_page)
    interpretation = paginator.page(pindex)
    page_json = []
    for item in interpretation.object_list:
        rst = item.to_hash()
        # rst.update({
        #     "is_like": item.is_like(p.id),
        #     "is_favor": item.is_favor(p.id),
        # })
        page_json.append(rst)
    return success_api_response({
        "interpretations": page_json,   # list of interpretation
        "has_next": interpretation.has_next(),
        "has_previous": interpretation.has_previous(),
        "page_now": interpretation.number,    # total
        "page_total": paginator.num_pages,
        "interpretation_total": interpretation_num,  # total amount of inter
    })


INTERPRETATION_API = wrapped_api({
    # 'POST': create_paper,
    # 'DELETE': delete_paper,
    # 'PUT': update_micro_evidence,
    'GET': get_interpretation_by_id
})
