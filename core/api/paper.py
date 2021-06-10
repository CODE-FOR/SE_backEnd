from django.views.decorators.http import require_http_methods
from django.http import HttpRequest

from .utils import (failed_api_response, ErrorCode,
                    success_api_response,
                    wrapped_api, response_wrapper)
import json

from core.models.tag import Tag, TAG, KEYWORD
from core.models.user import User

from core.api.auth import jwt_auth
from core.models.paper import Paper, get_paper_ordered_dec, get_paper_title_and_id, Paper_report, get_all_paper_report
from django.core.paginator import Paginator
from core.models.interpretation import Interpretation
import time


# paper curd


@response_wrapper
@jwt_auth()
@require_http_methods('POST')
def create_paper(request: HttpRequest):
    """
    :param request:
        title: string
        abstract: string
        author: list of string
        source: url
        published_year: int
        topic: list of string
        tags: list of string

    :return:
        paper_id
    """
    params = json.loads(request.body.decode())
    user = request.user
    if params.get('user_id'):
        user = User.objects.get(pk=params.get('user_id'))

    if user.is_banned:
        return failed_api_response(ErrorCode.BANNED, "user banned")

    limits = Paper.objects.filter(created_by=user).order_by('-created_at')
    if limits.count() >= 5:
        limit_time = limits[4].created_at.timestamp()
        now_time = time.time()
        if now_time - limit_time <= 3600:
            return failed_api_response(ErrorCode.LIMIT, "reach post limit in an hour")

    paper = Paper()
    paper.title = params.get("title")
    paper.source = params.get("source")
    paper.published_year = params.get("published_year")
    paper.abstract = params.get("abstract")
    paper.created_by = user
    paper.save()

    paper.add_author(params.get("author"))

    # for recommend
    # tags = user.user_tags[1:-1]
    # tags_arr: list = [0] * 70 if tags == '' else [int(s) for s in tags.split(',')]
    # end

    for tag in params.get("tags"):
        tag_name = tag.get('name', None)
        tag_type = tag.get('type', None)
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
        paper.tag_list.add(tag)
        # if tag_type == 0:
        #     tags_arr[tag.id] += 1

    # user.user_tags = tags_arr
    # user.save()

    return success_api_response({
        "id": paper.id
    })


@response_wrapper
@jwt_auth()
@require_http_methods('POST')
def delete_paper(request: HttpRequest):
    """ delete paper
    :param request:
        paperId: id of paper
        reason: reason
    :return:
    """
    params = json.loads(request.body.decode())

    paper = Paper.objects.get(pk=params.get("paperId"))

    p = request.user

    paper.safe_delete(params.get("reason"))

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
    rst = paper.to_hash(p)

    if paper.is_deleted:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, "Bad Paper ID.")

    interpretations = paper.get_related_interpretation(p)

    rst.update({
        "interpretations": interpretations,
        #     "is_like": micro_evidence.is_like(p.id,
        #     "is_favor": micro_evidence.is_favor(p.id),
    })
    return success_api_response(rst)


@response_wrapper
@jwt_auth()
@require_http_methods('GET')
def like_paper(request: HttpRequest, id: int):
    """ get micro evidence information
    :param request:
    :param id: primary key
    :return:
    """
    p = request.user
    paper = Paper.objects.get(pk=id)

    paper.be_liked(p)

    return success_api_response({})


@response_wrapper
@jwt_auth()
@require_http_methods('GET')
def collect_paper(request: HttpRequest, id: int):
    """ get micro evidence information
    :param request:
    :param id: primary key
    :return:
    """
    p = request.user
    paper = Paper.objects.get(pk=id)

    paper.be_collected(p)

    return success_api_response({})


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
    params = request.GET.dict()

    papers = get_paper_ordered_dec()
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
        rst = item.to_hash(p)
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
        "page_num": paginator.num_pages,    # total
        "paper_num": paper_num,
    })


@response_wrapper
@jwt_auth()
@require_http_methods('GET')
def get_paper_title(request: HttpRequest):
    titles = get_paper_title_and_id()
    return success_api_response({
        "titles": titles
    })


@response_wrapper
@jwt_auth()
@require_http_methods('POST')
def cancel_report_paper(request: HttpRequest):
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

    report = Paper_report.objects.get(pk=report_id)

    report.solve()

    return success_api_response({
    })


@response_wrapper
@jwt_auth()
@require_http_methods('POST')
def report_paper(request: HttpRequest):
    """
    :param request:
        paperId: paper id
        reason: reason

    :return:
        report_id
    """
    params = json.loads(request.body.decode())
    user = request.user

    paper_id = params.get("paperId")
    reason = params.get("reason")

    paper = Paper.objects.filter(pk=paper_id)
    if paper.exists():
        paper = paper.first()
    else:
        return failed_api_response(ErrorCode.ID_NOT_EXISTS, "invalid paper id")

    report_id = paper.be_reported(user, reason)

    return success_api_response({
        "id": report_id
    })


@response_wrapper
@jwt_auth()
@require_http_methods('GET')
def list_paper_report(request: HttpRequest, pindex):
    """
    get a page as order in time
    :param request:
        user_id: request user id
    :param pindex: page index
    :return:
    """
    params = request.GET.dict()

    reports = get_all_paper_report()
    report_num = Paper_report.objects.filter(paper_id__is_deleted=False).count()
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
        "number": report_page.number,   # page current
        "page_num": paginator.num_pages,    # total pages
        "report_num": report_num,   # total number of reports
    })


PAPER_API = wrapped_api({
    'POST': create_paper,
    'DELETE': delete_paper,
    # 'PUT': update_micro_evidence,
    'GET': get_signal_paper
})

