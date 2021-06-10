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
from core.models.interpretation import Interpretation, get_interpretation_ordered, get_all_interpretation_report, \
    Interpretation_report
import time, random


# interpretation curd


DEFAULT_WEIGHT = 1
PAPER_WEIGHT = 100
INTER_WEIGHT = 50


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

    if user.is_banned:
        return failed_api_response(ErrorCode.BANNED, "user banned")

    limits = Interpretation.objects.filter(created_by=user).order_by('-created_at')
    if limits.count() >= 5:
        limit_time = limits[4].created_at.timestamp()
        now_time = time.time()
        if now_time - limit_time <= 3600:
            return failed_api_response(ErrorCode.LIMIT, "reach post limit in an hour")

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
def like_interpretation(request: HttpRequest, id: int):
    """ get micro evidence information
    :param request:
    :param id: primary key
    :return:
    """
    p = request.user
    interpretation = Interpretation.objects.get(pk=id)

    interpretation.be_liked(p)

    return success_api_response({})


@response_wrapper
@jwt_auth()
@require_http_methods('GET')
def collect_interpretation(request: HttpRequest, id: int):
    """ get micro evidence information
    :param request:
    :param id: primary key
    :return:
    """
    p = request.user
    interpretation = Interpretation.objects.get(pk=id)

    interpretation.be_collected(p)

    return success_api_response({})


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
    if interpretation.is_deleted:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, "Bad Interpretation ID.")
    rst = interpretation.to_hash(p)

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
        rst = item.to_hash(p)
        # rst.update({
        #     "is_like": item.is_like(p.id),
        #     "is_favor": item.is_favor(p.id),
        # })
        page_json.append(rst)
    return success_api_response({
        "interpretations": page_json,  # list of interpretation
        "has_next": interpretation.has_next(),
        "has_previous": interpretation.has_previous(),
        "page_now": interpretation.number,  # total
        "page_total": paginator.num_pages,
        "interpretation_total": interpretation_num,  # total amount of inter
    })


@response_wrapper
@jwt_auth()
@require_http_methods('POST')
def delete_interpretation(request: HttpRequest):
    """ delete interpretation
    :param request:
        interpretationId: id of paper
        reason: reason
    :return:
    """
    params = json.loads(request.body.decode())

    interpretation = Interpretation.objects.get(pk=params.get("interpretationId"))

    p = request.user

    interpretation.safe_delete(params.get("reason"))

    return success_api_response({})


@response_wrapper
@jwt_auth()
@require_http_methods('POST')
def report_interpretation(request: HttpRequest):
    """
    :param request:
        interpretationId: interpretation id
        reason: reason

    :return:
        report_id
    """
    params = json.loads(request.body.decode())
    user = request.user

    interpretation_id = params.get("interpretationId")
    reason = params.get("reason")

    interpretation = Interpretation.objects.filter(pk=interpretation_id)
    if interpretation.exists():
        interpretation = interpretation.first()
    else:
        return failed_api_response(ErrorCode.ID_NOT_EXISTS, "invalid interpretation id")

    report_id = interpretation.be_reported(user, reason)

    return success_api_response({
        "id": report_id
    })


@response_wrapper
@jwt_auth()
@require_http_methods('POST')
def cancel_report_interpretation(request: HttpRequest):
    """
    :param request:
        reportId: report id
        reason: reason

    :return:
    """
    params = json.loads(request.body.decode())
    user = request.user

    report_id = params.get("reportId")
    reason = params.get("reason")

    report = Interpretation_report.objects.get(pk=report_id)

    report.solve()

    return success_api_response({
    })


@response_wrapper
@jwt_auth()
@require_http_methods('GET')
def list_interpretation_report(request: HttpRequest, pindex):
    """
    get a page as order in time
    :param request:
        user_id: request user id
    :param pindex: page index
    :return:
    """
    params = request.GET.dict()

    reports = get_all_interpretation_report()
    report_num = Interpretation_report.objects.filter(interpretation_id__is_deleted=False).count()
    p = request.user
    if params.get('user_id'):
        p = User.objects.get(pk=params.get('user_id'))
    num_per_page = 5
    if params.get('num_per_page', None):
        num_per_page = int(params.get('num_per_page', None))
    paginator = Paginator(reports, num_per_page)
    report_page = paginator.page(pindex)
    page_json = []
    for item in report_page.object_list:
        rst = item.to_hash(p)
        page_json.append(rst)
    return success_api_response({
        "reports": page_json,
        "has_next": report_page.has_next(),
        "has_previous": report_page.has_previous(),
        "number": report_page.number,  # page current
        "page_num": paginator.num_pages,  # total pages
        "report_num": report_num,  # total number of reports
    })


INTERPRETATION_API = wrapped_api({
    # 'POST': create_paper,
    # 'DELETE': delete_paper,
    # 'PUT': update_micro_evidence,
    'GET': get_interpretation_by_id
})


@response_wrapper
@jwt_auth()
@require_http_methods('GET')
def recommend_inter(request: HttpRequest):
    """
    :param request:
        None
    :return:
    """

    user = request.user

    prefer = dict()

    tags = Tag.objects.filter(type=0)
    for tag in tags:
        prefer[tag.pk] = 0

    collect_papers = user.collect_paper.all()
    for paper in collect_papers:
        for tag in paper.tag_list.filter(type=0):
            prefer[tag.pk] += PAPER_WEIGHT

    collect_interpretations = user.collect_interpretation.all()
    for interpretation in collect_interpretations:
        paper = interpretation.paper
        for tag in paper.tag_list.filter(type=0):
            prefer[tag.pk] += INTER_WEIGHT

    all_inter = []
    weight = []

    for interpretation in Interpretation.objects.filter(is_deleted=False):
        w = DEFAULT_WEIGHT
        paper = interpretation.paper
        for tag in paper.tag_list.filter(type=0):
            w += prefer[tag.pk]
        all_inter.append(interpretation)
        weight.append(w)

    recommend = []
    num = 5
    while num != 0:
        t = random.randint(0, sum(weight) - 1)
        for i, val in enumerate(weight):
            t -= val
            if t < 0:
                if all_inter[i] not in recommend:
                    recommend.append(all_inter[i])
                    num -= 1
                break

    inters = []

    for i in recommend:
        inters.append(i.to_hash(user))

    return success_api_response({
        "recommend": inters,
    })
