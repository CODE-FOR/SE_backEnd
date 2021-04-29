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
        return failed_api_response(ErrorCode.ITEM_ALREADY_EXISTS, "paper id doesn't exist!")
    interpretation.paper = paper
    interpretation.created_by = user
    interpretation.save()

    return success_api_response({
        "id": interpretation.id
    })


@response_wrapper
@jwt_auth()
@require_http_methods('DELETE')
def delete_paper(request: HttpRequest, id: int):
    """ delete paper
    :param request:
    :param id: primary key
    :return:
    """
    paper = Paper.objects.get(pk=id)

    current_user = request.user

    # for recommend
    # tags = current_user.user_tags[1:-1]
    # tags_arr: list = [0] * 70 if tags == '' else [int(s) for s in tags.split(',')]
    # mk_tags = micro_evidence.tag_list.all()
    # for tag in mk_tags:
    #     if tag.type == 0:
    #         tags_arr[tag.id] -= 1
    # current_user.user_tags = tags_arr
    # current_user.save()
    # end

    # if current_user == paper.created_by

    paper.is_deleted = True
    paper.save()

    return success_api_response({})


@response_wrapper
@jwt_auth()
@require_http_methods('GET')
def get_signal_paper(request: HttpRequest, id: int):
    """ get micro evidence information
    :param request:
    :param id: primary key
    :return:
    """
    p = request.user
    paper = Paper.objects.get(pk=id)
    rst = paper.to_hash()
    # rst.update({)
    #     "is_like": micro_evidence.is_like(p.id,
    #     "is_favor": micro_evidence.is_favor(p.id),
    # })
    return success_api_response(rst)


@response_wrapper
@jwt_auth()
@require_http_methods('GET')
def list_paper_page(request: HttpRequest, pindex):
    """
    get a page as order in time
    :param request:
        user_id: request user id
    :param pindex: page index
    :return:
    """
    params = dict(request.GET)

    papers = get_up()
    paper_num = Paper.objects.count()
    p = request.user
    if params.get('user_id'):
        p = User.objects.get(pk=params.get('user_id'))
    num_per_page = 5
    if params.get('num_per_page', None):
        num_per_page = int(params.get('num_per_page', None))
    paginator = Paginator(papers, num_per_page)
    paper = paginator.page(pindex)
    page_json = []
    for item in paper.object_list:
        rst = item.to_hash()
        # rst.update({
        #     "is_like": item.is_like(p.id),
        #     "is_favor": item.is_favor(p.id),
        # })
        page_json.append(rst)
    return success_api_response({
        "papers": page_json,
        "has_next": paper.has_next(),
        "has_previous": paper.has_previous(),
        "number": paper.number,
        "page_num": paginator.num_pages,
        "paper_num": paper_num,
    })


PAPER_API = wrapped_api({
    'POST': create_paper,
    'DELETE': delete_paper,
    # 'PUT': update_micro_evidence,
    'GET': get_signal_paper
})
