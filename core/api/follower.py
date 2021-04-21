from django.http import HttpRequest
from django.views.decorators.http import require_GET
from django.core.paginator import Paginator
from core.api.query_utils import query_page
from core.api.auth import jwt_auth
from core.api.utils import response_wrapper, success_api_response, failed_api_response, ErrorCode
from core.models.user import User

@response_wrapper
@jwt_auth()
@require_GET
@query_page()
def list_followers(request: HttpRequest, uid: int, *args, **kwargs):
    """list fans

    Arguments:
        request {HttpRequest} -- GET
    """
    if User.objects.filter(id=uid).exists() is False:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, 'User not found!')
    user = User.objects.get(id=uid)
    models_all = user.followers.count()
    models = user.followers.all()
    page = kwargs.get('page')
    page_size = kwargs.get('page_size')
    paginator = Paginator(models, page_size)
    page_all = paginator.num_pages

    if page > page_all:
        models_info = []
    else:
        models_info = list(
            paginator.get_page(page).object_list.values(
                'id', 'username', 'email', 'nick_name', 'institution'
            )
        )
    data = {
        'models_all': models_all,
        'total_count': paginator.count,
        'page_all': page_all,
        'page_now': page,
        'models': models_info
    }
    return success_api_response(data)
