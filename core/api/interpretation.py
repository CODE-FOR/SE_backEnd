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

