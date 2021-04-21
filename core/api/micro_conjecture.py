from django.views.decorators.http import require_http_methods
from django.http import HttpRequest
from django.forms import model_to_dict
from django.core.paginator import Paginator
from django.core import serializers
from .utils import (failed_api_response, ErrorCode,
                       success_api_response,
                       wrapped_api, response_wrapper)
import json
from core.models.micro_conjecture import MicroConjecture
from core.models.micro_evidence import MicroEvidence
from core.models.micro_knowledge import (JUDGE_STATUS_CHIOCES, JUDGING)
from core.models.user import User
from core.models.tag import Tag, TAG, KEYWORD
from core.api.auth import jwt_auth


# micro conjecture curd

@response_wrapper
@jwt_auth()
@require_http_methods('POST')
def create_micro_conjecture(request: HttpRequest):
    """
    :param request:
        content

        tags:
            name: string
        citations:
            cited paper: string
            source: url
            published_year: datetime
        evidences:
            micro_evidence_id
    :return:
        micro_conjecture_id
    """
    params = json.loads(request.body.decode())
    user = request.user

    micro_conjecture = MicroConjecture()
    micro_conjecture.content = params.get("content")
    micro_conjecture.created_by = user
    micro_conjecture.judge_status = JUDGING
    micro_conjecture.save()
    
    # for recommend
    tags = user.user_tags[1:-1]
    tags_arr: list = [0]*70 if tags == '' else [int(s) for s in tags.split(',')]
    # end

    for tag_params in params.get("tags"):
        tag_name = tag_params.get('name', None)
        tag_type = tag_params.get('type', None)
        if tag_name is None:
            return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, "tag params miss argument: tag_name.")
        if tag_type is None:
            return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, "tag params miss argument: tag_type.")
        if Tag.objects.filter(type=TAG).filter(name=tag_name).exists():
            tag = Tag.objects.filter(type=TAG).filter(name=tag_name).first()
        elif Tag.objects.filter(type=KEYWORD).filter(name=tag_name).exists():
            tag = Tag.objects.filter(type=KEYWORD).filter(name=tag_name).first()
        else:
            tag = Tag(name=tag_name, type=tag_type)
            tag.save()
        micro_conjecture.tag_list.add(tag)
        if tag_type == 0:
            tags_arr[tag.id] += 1
    
    user.user_tags = tags_arr
    user.save()

    for evidence_id in params.get("evidences"):
        evidence = MicroEvidence.objects.get(pk=evidence_id)
        if evidence is not None:  # TODO : do this is the commanded method
            micro_conjecture.evidences.add(evidence)

    return success_api_response({
        "id": micro_conjecture.id
    })


@response_wrapper
@jwt_auth()
@require_http_methods('DELETE')
def delete_micro_conjecture(request: HttpRequest, id: int):
    """ delete micro conjecture
    :param request:
    :param id: primary key
    :return:
    """
    micro_conjecture = MicroConjecture.objects.get(pk=id)
    current_user = request.user
    # for recommend
    tags = current_user.user_tags[1:-1]
    tags_arr: list = [0]*70 if tags == '' else [int(s) for s in tags.split(',')]
    mk_tags = micro_conjecture.tag_list.all()
    for tag in mk_tags:
        if tag.type == 0:
            tags_arr[tag.id] -= 1
    current_user.user_tags = tags_arr
    current_user.save()
    # end
    micro_conjecture.delete()

    return success_api_response({})


@response_wrapper
@jwt_auth()
@require_http_methods('PUT')
def update_micro_conjecture(request: HttpRequest, id: int):
    """ update micro conjecture
    :param request:
    :param id: primary key
    :return:
    """
    params = json.loads(request.body.decode())
    micro_conjecture = MicroConjecture.objects.get(pk=id)
    for key in params.keys():
        setattr(micro_conjecture, key, params.get(key))
    micro_conjecture.save()
    return success_api_response({})


@response_wrapper
@jwt_auth()
@require_http_methods('GET')
def get_micro_conjecture(request: HttpRequest, id: int):
    """ get micro conjecture information
    :param request:
    :param id: primary key
    :return:
    """
    p = request.user
    micro_conjecture = MicroConjecture.objects.get(pk=id)
    rst = micro_conjecture.to_hash()
    rst.update({
        "is_like": micro_conjecture.is_like(p.id),
        "is_favor": micro_conjecture.is_favor(p.id),
    })
    return success_api_response(rst)


@response_wrapper
@jwt_auth()
@require_http_methods('GET')
def list_micro_conjecture(request: HttpRequest, pindex):
    """
    get a page
    :param request:
        keywords: list of string
        tags: list of string
        num_per_page: num_per_page
        user_id: request user id
    :param pindex: page index
    :return:
    """
    params = request.GET.dict()
    micro_conjecture_list = MicroConjecture.search_by_keywords_and_tags(keywords=params.get('keywords', None),
                                                                       tags=params.get('tags', None))
    p = request.user
    if params.get('user_id'):
        p = User.objects.get(pk=params.get('user_id'))
    num_per_page = 20
    if params.get('num_per_page', None):
        num_per_page = int(params.get('num_per_page', None))
    paginator = Paginator(micro_conjecture_list, num_per_page)
    micro_conjecture_page = paginator.page(pindex)
    page_json = []
    for item in micro_conjecture_page.object_list:
        rst = item.to_hash()
        rst.update({
            "is_like": item.is_like(p.id),
            "is_favor": item.is_favor(p.id),
        })
        page_json.append(rst)
    return success_api_response({
        "page": page_json,
        "has_next": micro_conjecture_page.has_next(),
        "has_previous": micro_conjecture_page.has_previous(),
        "number": micro_conjecture_page.number,
        "page_num": paginator.num_pages,
    })


MICRO_CONJECTURE_API = wrapped_api({
    'POST': create_micro_conjecture,
    'DELETE': delete_micro_conjecture,
    'PUT': update_micro_conjecture,
    'GET': get_micro_conjecture
})

MICRO_CONJECTURE_SET_API = wrapped_api({
    'GET': list_micro_conjecture
})
