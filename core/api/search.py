from django.views.decorators.http import require_http_methods
from django.http import HttpRequest

from .utils import (failed_api_response, ErrorCode,
                    success_api_response,
                    wrapped_api, response_wrapper)
import json

from core.models.tag import Tag, TAG, KEYWORD
from core.models.user import User

from core.api.auth import jwt_auth
from core.models.paper import Paper, get_up, get_title_and_id
from core.models.interpretation import Interpretation
from django.core.paginator import Paginator


# search


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
