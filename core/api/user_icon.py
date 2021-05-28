from core.models.user import User
from django.http.request import HttpRequest
from core.api.utils import (require_http_methods, ErrorCode,
                            response_wrapper, wrapped_api,
                            success_api_response, failed_api_response)
from core.api.auth import jwt_auth
from ..models.user import User


@jwt_auth()
@response_wrapper
@require_http_methods('GET')
def get_user_icon(request: HttpRequest):
    """
    get user icon
    :param request:
    :return:
    """
    p = request.user
    return success_api_response({
        "icon": str(p.icon),
    })


@jwt_auth()
@response_wrapper
@require_http_methods('GET')
def get_icon_by_id(request: HttpRequest):
    """
    get icon by id
    :param request:
        id: user id
    :return: icon
    """
    user_id = request.GET.dict().get('id')




@jwt_auth()
@response_wrapper
@require_http_methods('POST')
def change_user_icon(request: HttpRequest):
    """
    change user icon
    :param request:
        FILES: icon: new user icon
    :return:
    """
    # icon = request.FILES.get("icon", None)
    icon = request.POST.dict().get('icon')
    print(icon)
    if icon is None:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, "user icon has not provided.")

    p = request.user
    p.icon = icon
    p.save()
    # try:
    #     p.save()
    # except Exception:
    #     return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, "set user icon error.")
    return success_api_response({
        "message": "user icon set success."
    })


USER_ICON_API = wrapped_api({
    "GET": get_user_icon,
    "POST": change_user_icon,
})
