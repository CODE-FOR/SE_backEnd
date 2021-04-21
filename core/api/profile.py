
from django.http import HttpRequest
from django.views.decorators.http import require_GET
from core.api.auth import jwt_auth
from core.api.utils import (ErrorCode, failed_api_response, parse_data,
                            response_wrapper, success_api_response)
from core.models.user import User

@response_wrapper
@jwt_auth()
@require_GET
def get_profile(request: HttpRequest):
    data: dict = request.GET.dict()
    user = request.user
    if data is not None:
        user_id = data.get('user_id')
        if user_id is not None:
            if User.objects.filter(pk=user_id).exists() is False:
                return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, 'User is not exist')
            user = User.objects.get(pk=user_id)
    all_post = user.created_by.all().distinct()
    total_like = 0
    for post in all_post:
        total_like += post.like_list.count()
    data = {
        'id': user.id,
        'username': user.username,
        'icon': str(user.icon),
        'is_sponsor': user.is_sponsor,
        'nickname': user.nick_name,
        'email': user.email,
        'institution': user.institution,
        'total_post': user.created_by.count(),
        'total_like': total_like,
        'total_fan': user.user_set.count(),
        'is_following': user.user_set.filter(id=request.user.id).exists(),
        'is_followed': user.followers.filter(id=request.user.id).exists()
    }
    return success_api_response(data)
