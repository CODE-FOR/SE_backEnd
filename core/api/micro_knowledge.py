from django.views.decorators.http import require_http_methods
from django.http import HttpRequest
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.forms import model_to_dict
from .utils import (failed_api_response,
                       success_api_response,
                       wrapped_api, response_wrapper,ErrorCode)
from core.models.micro_evidence import MicroEvidence
from core.models.micro_conjecture import MicroConjecture
from core.models.micro_knowledge import (MicroKnowledge, JUDGE_STATUS_CHIOCES, JUDGING, FAILED, PASSED)
from core.models.notification import (Notification, MICRO_KNOWLEDGE_FAVOR, MICRO_KNOWLEDGE_LIKE)
from core.models.user import User
from core.api.auth import jwt_auth


@response_wrapper
@jwt_auth()
@require_http_methods('POST')
def favor(request: HttpRequest, eid):
    """ like a micro_knowledge
    :param request:
    :param eid: micro_knowledge id
    :return:
    """
    current_user = request.user
    micro_knowledge = MicroKnowledge.objects.get(pk=eid)
    current_user.favorites.add(micro_knowledge)

    Notification.new_notification(
        code=MICRO_KNOWLEDGE_FAVOR,
        from_user=current_user,
        to_user=micro_knowledge.created_by,
        content="Your micro knowledge has been favored.",
        micro_knowledge=micro_knowledge,
    )
    
    # for recommend
    tags = current_user.user_tags[1:-1]
    tags_arr: list = [0]*70 if tags == '' else [int(s) for s in tags.split(',')]
    mk_tags = micro_knowledge.tag_list.all()
    for tag in mk_tags:
        if tag.type == 0:
            tags_arr[tag.id] += 1
    current_user.user_tags = tags_arr
    current_user.save()
    # end
    return success_api_response({})


@response_wrapper
@jwt_auth()
@require_http_methods('POST')
def unfavor(request: HttpRequest, eid : int):
    """ like a micro_knowledge
    :param request:
    :param eid: micro_knowledge id
    :return:
    """
    current_user = request.user
    micro_acknowledge = MicroKnowledge.objects.get(pk=eid)
    current_user.favorites.remove(micro_acknowledge)
    
    # for recommend
    tags = current_user.user_tags[1:-1]
    tags_arr: list = [0]*70 if tags == '' else [int(s) for s in tags.split(',')]
    mk_tags = micro_acknowledge.tag_list.all()
    for tag in mk_tags:
        if tag.type == 0:
            tags_arr[tag.id] -= 1
    current_user.user_tags = tags_arr
    current_user.save()
    # end
    
    return success_api_response({})


@response_wrapper
@jwt_auth()
@require_http_methods('GET')
def list_favorites(request: HttpRequest, pindex : int):
    """ get favor list
    :param request:
        num_per_page: num_per_page
        user_id: quest user
        micro_evidence: boolean, get micro evidence
        micro_conjecture: boolean, get micro conjecture
    :param pindex: which page
    :return:
    """
    # some api will be used in method
    def getTime(elem):
        from datetime import datetime
        created_at_time = elem.get('created_at', None)
        if created_at_time and created_at_time.__class__ == datetime:
            return created_at_time
        else:
            return datetime.now()
    # basic params
    params = request.GET.dict()
    num_per_page = 20
    if params.get('num_per_page', None):
        num_per_page = int(params.get('num_per_page', None))
    if num_per_page <= 0:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, "num_per_page should be bigger than 0.")
    p = request.user
    current_user = request.user
    if params.get('user_id', None):
        try:
            p = User.objects.get(pk=params.get('user_id', None))
        except Exception:
            return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, "asked user not exist.")
    # make list
    favorites_list = []
    if params.get('micro_evidence', None) == "true":
        micro_evidence_list = MicroEvidence.objects.filter(pk__in=p.favorites.values('id'))
        for micro_evidence in micro_evidence_list:
            rst = micro_evidence.to_hash()
            rst.update({
                "is_like": micro_evidence.is_like(current_user.id),
                "is_favor": micro_evidence.is_favor(current_user.id),
            })
            favorites_list.append(rst)
    if params.get('micro_conjecture', None) == "true":
        micro_conjecture_list = MicroConjecture.objects.filter(pk__in=p.favorites.values('id'))
        for micro_conjecture in micro_conjecture_list:
            rst = micro_conjecture.to_hash()
            rst.update({
                "is_like": micro_conjecture.is_like(current_user.id),
                "is_favor": micro_conjecture.is_favor(current_user.id),
            })
            favorites_list.append(rst)
    favorites_list.sort(key=getTime, reverse=True)
    # paginate
    paginator = Paginator(favorites_list, num_per_page)
    favorites_page = paginator.page(pindex)
    return success_api_response({
        "page": list(favorites_page),
        "has_next": favorites_page.has_next(),
        "has_previous": favorites_page.has_previous(),
        "number": favorites_page.number,
        "page_num": paginator.num_pages,
    })


@jwt_auth()
@response_wrapper
@require_http_methods('POST')
def like_micro_knowledge(request: HttpRequest, id: int):
    """
    like a micro_knowledge
    
    [method]: POST
    
    parms:
    """
    current_user = request.user
 
    try:
        mk = MicroKnowledge.objects.get(id=id)
    except ObjectDoesNotExist:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, "Bad Knowledge ID.")
    like_user = mk.like_list.filter(id = current_user.id)
    # for recommend
    tags = current_user.user_tags[1:-1]
    tags_arr: list = [0]*70 if tags == '' else [int(s) for s in tags.split(',')]
    mk_tags = mk.tag_list.all()

    if like_user.count() == 0:

        Notification.new_notification(
            code=MICRO_KNOWLEDGE_LIKE,
            from_user=current_user,
            to_user=mk.created_by,
            content="Your micro knowledge has a new like.",
            micro_knowledge=mk,
        )

        mk.like_list.add(current_user)
        for tag in mk_tags:
            if tag.type == 0:
                tags_arr[tag.id] += 1
    else:
        mk.like_list.remove(current_user)
        for tag in mk_tags:
            if tag.type == 0:
                tags_arr[tag.id] -= 1
    
    current_user.user_tags = tags_arr
    current_user.save()
    # end
    return success_api_response({})


@response_wrapper
@jwt_auth()
@require_http_methods('GET')
def list_micro_knowledge(request: HttpRequest, pindex: int):
    """ get favor list
    :param request:
        num_per_page: num_per_page
        micro_evidence: boolean, get micro evidence
        micro_conjecture: boolean, get micro conjecture
        judge_status: int, choose judge_status
        user_id: int, which user content
        keywords: list of str, search keywords
        tags: list of str, search tags
    :param pindex: which page
    :return:
    """
    # some api will be used in method
    def getTime(elem):
        from datetime import datetime
        created_at_time = elem.get('created_at', None)
        if created_at_time and created_at_time.__class__ == datetime:
            return created_at_time
        else:
            return datetime.now()

    def getId(elem):
        return elem.id

    # basic params
    params = request.GET.dict()
    num_per_page = 20
    if params.get('num_per_page', None):
        num_per_page = int(params.get('num_per_page', None))
    if num_per_page <= 0:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, "num_per_page should be bigger than 0.")
    judge_status = None
    if not params.get('judge_status', None) in [None, str(JUDGING), str(PASSED), str(FAILED)]:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, "invalid judge status is requested.")
    else:
        judge_status = None if params.get('judge_status', None) is None else int(params.get('judge_status', None))
    current_user = request.user

    # prepare query set
    micro_evidence_objects = MicroEvidence\
        .search_by_keywords_and_tags(keywords=params.get('keywords', None), tags=params.get('tags', None))\
        .exclude(created_by=current_user)
    micro_conjecture_objects = MicroConjecture\
        .search_by_keywords_and_tags(keywords=params.get('keywords', None), tags=params.get('tags', None))\
        .exclude(created_by=current_user)
    if params.get('user_id'):
        try:
            p = User.objects.get(pk=params.get('user_id'))
            micro_evidence_objects = micro_evidence_objects.filter(created_by=p)
            micro_conjecture_objects = micro_conjecture_objects.filter(created_by=p)
        except Exception:
            return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, "invalid request user.")
    if judge_status is not None:
        micro_evidence_objects = micro_evidence_objects.filter(judge_status=judge_status)
        micro_conjecture_objects = micro_conjecture_objects.filter(judge_status=judge_status)

    # make list
    micro_knowledge_list = []
    if params.get('micro_evidence', None) == "true":
        for micro_evidence in micro_evidence_objects:
            if (not (judge_status is None)) and ((current_user in micro_evidence.pass_voter.all()) or
                                                 (current_user in micro_evidence.unpass_voter.all())):
                continue
            micro_knowledge_list.append(micro_evidence)
    if params.get('micro_conjecture', None) == "true":
        for micro_conjecture in micro_conjecture_objects:
            if (not (judge_status is None)) and ((current_user in micro_conjecture.pass_voter.all()) or
                                                 (current_user in micro_conjecture.unpass_voter.all())):
                continue
            micro_knowledge_list.append(micro_conjecture)
    micro_knowledge_list.sort(key=getId, reverse=True)

    # paginate
    paginator = Paginator(micro_knowledge_list, num_per_page, allow_empty_first_page=True)
    recent_page = paginator.page(int(pindex))

    # modify return msg
    rst_page_list = []
    for micro_knowledge in recent_page:
        rst = micro_knowledge.to_hash()
        rst.update({
            "is_like": micro_knowledge.is_like(current_user),
            "is_favor": micro_knowledge.is_favor(current_user.id),
        })
        rst_page_list.append(rst)

    return success_api_response({
        "page": rst_page_list,
        "has_next": recent_page.has_next(),
        "has_previous": recent_page.has_previous(),
        "number": recent_page.number,
        "page_num": paginator.num_pages,
    })


FAVORITES_SET_API = wrapped_api({
    'GET': list_favorites,
})

MICRO_KNOWLEDGE_SET_API = wrapped_api({
    'GET': list_micro_knowledge,
})