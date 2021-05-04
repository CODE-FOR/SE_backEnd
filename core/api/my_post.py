from django.http import HttpRequest
from django.db.models import Count
from django.views.decorators.http import require_GET
from django.core.paginator import Paginator
from core.api.query_utils import query_page
from core.api.auth import jwt_auth
from core.api.utils import (ErrorCode, failed_api_response, parse_data,
                            response_wrapper, success_api_response)

from core.models.micro_knowledge import MicroKnowledge
from core.models.user import User


@response_wrapper
@jwt_auth()
@require_GET
@query_page()
def list_posts(request: HttpRequest, uid: int, *args, **kwargs):
    """list fans

    Arguments:
        request {HttpRequest} -- GET
    """
    if User.objects.filter(id=uid).exists() is False:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, 'User not found!')
    user = User.objects.get(id=uid)
    models_all = user.created_by.count()
    if uid == request.user.id:
        models = user.created_by.all().order_by('-id').distinct()
    else:
        models = user.created_by.filter(judge_status=1).order_by('-id').distinct()
    page = kwargs.get('page')
    page_size = kwargs.get('page_size')
    paginator = Paginator(models, page_size)
    page_all = paginator.num_pages

    if page > page_all:
        models_info = []
    else:
        models_info = list(
            paginator.get_page(page).object_list.values(
                'id', 'created_at', 'content', 'judge_status',
                'microconjecture', 'microevidence'
            )
        )

    for item in models_info:
        item['like_num'] = MicroKnowledge.objects.get(id=item["id"]).like_num()
        item['favor_num'] = MicroKnowledge.objects.get(id=item["id"]).favorites_num()
    data = {
        'models_all': models_all,
        'total_count': paginator.count,
        'page_all': page_all,
        'page_now': page,
        'models': models_info
    }
    return success_api_response(data)
