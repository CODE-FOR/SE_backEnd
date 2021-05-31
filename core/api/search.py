from django.views.decorators.http import require_http_methods
from django.http import HttpRequest

from .utils import (failed_api_response, ErrorCode,
                    success_api_response,
                    wrapped_api, response_wrapper)
import json

from core.models.tag import Tag, TAG, KEYWORD
from core.models.user import User

from core.api.auth import jwt_auth
from core.models.paper import Paper
from core.models.interpretation import Interpretation
from django.core.paginator import Paginator
from core.api.common import search_by_keyword_and_tags


# search


@response_wrapper
@jwt_auth()
@require_http_methods('GET')
def search_by_tag(request: HttpRequest, pindex):
    """
    get a page as order in time
    :param request:
        user_id: request user id
        pindex: page num
        keywords: keyword, string, search by this
        tags: tags, string, in format "id1 + id2"
        paper: find paper, bool
        interpretaion: find interpretation, bool
    :param pindex: page index
    :return:
    """
    p = request.user

    cls = type
    params = request.GET.dict()

    is_paper = params.get('paper')
    # rint(type(is_paper))
    is_interpretation = params.get('interpretation')
    # print(is_interpretation)
    pindex = params.get('pindx')
    if is_paper is 'true':
        # print('paper!')
        cls = Paper
    elif is_interpretation is 'true':
        # print('interpretation!')
        cls = Interpretation
    else:
        failed_api_response (ErrorCode.INVALID_REQUEST_ARGS, "both paper and interpretaions is False!")

    tags = params.get('tags')

    if tags and tags is not '':
        tags = tags.split()
    else:
        tags = []

    keyword = params.get('keywords')

    items = search_by_keyword_and_tags(cls, tags, keyword)

    result_num = items.count()

    num_per_page = 5
    if params.get('num_per_page', None):
        num_per_page = int(params.get('num_per_page', None))

    paginator = Paginator(items, num_per_page)
    result = paginator.page(pindex)
    page_json = []
    for item in result.object_list:
        rst = item.to_hash(p)
        # rst.update({
        #     "is_like": item.is_like(p.id),
        #     "is_favor": item.is_favor(p.id),
        # })
        page_json.append(rst)
    return success_api_response({
        "total_res": result_num,
        "res": page_json,
    })
