from django.views.decorators.http import require_http_methods
from django.http import HttpRequest
from django.views.decorators.http import require_POST, require_GET
from django.core.exceptions import ObjectDoesNotExist
from .utils import (failed_api_response,
                    success_api_response,
                    wrapped_api, response_wrapper, ErrorCode, parse_data)
from core.models.micro_knowledge import MicroKnowledge,JUDGE_STATUS_CHIOCES
from core.models.user import User
from core.api.auth import jwt_auth
from django.forms import model_to_dict


@response_wrapper
@jwt_auth()
@require_POST
def judge_knowledge(request: HttpRequest, id: int):
    """
    judge a knowledge

    [method]: POST

    [url]: micro-knowledge/<int:id>/judge

    [parms]:
                - id: micro_knowledge id
        [args]:
                - passed: int
                - unpassed: int
    """
    data: dict = parse_data(request)
    current_user = request.user
    try:
        mk = MicroKnowledge.objects.get(id=id)
    except ObjectDoesNotExist:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, "Bad Knowledge ID.")
    if mk.judge_status != 0:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, "Knowledge has been judged.")
    if data is None:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, "Null body.")
    passed = data.get('passed')
    unpassed = data.get('unpassed')
    if not ((passed is None) ^ (unpassed is None)):
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, "Bad ARGS.")
    if mk.pass_voter.filter(id = current_user.id).exists() or mk.unpass_voter.filter(id = current_user.id).exists():
        return failed_api_response(ErrorCode.ITEM_ALREADY_EXISTS, "Have voted")
    if passed is not None and passed == 1:
        mk.pass_voter.add(current_user)
        if mk.pass_voter.count() >= 3:
            mk.judge_status = 1
            mk.save()
    elif unpassed is not None and unpassed == 1:
        mk.unpass_voter.add(current_user)
        if mk.unpass_voter.count() >= 3:
            mk.judge_status = -1
            mk.save()
    else:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, "Bad ARGS.")
    return success_api_response({})

@response_wrapper
@jwt_auth()
@require_GET
def get_judge_status(request: HttpRequest, id: int):
    """
    judge a knowledge

    [method]: GET

    [url]: micro-knowledge/<int:id>/judge

    [parms]:
        - id: micro_knowledge id
    """
    current_user = request.user
    try:
        mk = MicroKnowledge.objects.get(id=id)
    except ObjectDoesNotExist:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, "Bad Knowledge ID.")
    if mk.pass_voter.filter(id = current_user.id).exists():
        return success_api_response({'passed': 1})
    elif mk.unpass_voter.filter(id = current_user.id).exists():
        return success_api_response({'unpassed': 1})
    else:
        return success_api_response({})
    
MICRO_KNOWLEDGE_JUDGE_API = wrapped_api({
    'POST': judge_knowledge,
    'GET': get_judge_status,
})