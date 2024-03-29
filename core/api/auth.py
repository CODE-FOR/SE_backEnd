"""JSON Web Token API
Nowadays, it locates at {workspace}/core/api/
Maybe someday it will be moved to {workspace}/auth/
"""
from datetime import timedelta

import json
import jwt
from django.conf import settings
from django.contrib.auth import authenticate
from django.http import HttpRequest
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from core.api.utils import (ErrorCode, failed_api_response, response_wrapper,
                            success_api_response)
from core.models.auth_record import AuthRecord
from core.models.user import User


def auth_failed(message: str):
    """shorten
    """
    return failed_api_response(ErrorCode.UNAUTHORIZED, message)


def generate_access_token(user_id: int, access_token_delta: int = 1) -> str:
    """generate jwt

    Args:
        user_id (str): user.id
        access_token_delta (int, optional): time to expire. Defaults to 1 (hour).
    """
    current_time = timezone.now()
    access_token_payload = {
        "user_id": user_id,
        "exp": current_time + timedelta(hours=access_token_delta),
        "iat": current_time,
        "type": "access_token",
    }

    # return jwt.encode(access_token_payload, settings.SECRET_KEY, algorithm="HS256").decode("utf-8")
    return jwt.encode(access_token_payload, settings.SECRET_KEY, algorithm="HS256")


def generate_refresh_token(user: User, refresh_token_delta: int = 6 * 24) -> str:
    """generate jwt

    Args:
        user (User): User object
        refresh_token_delta (int, optional): time to expire. Defaults to 6 days (7 * 24 hours).
    """
    current_time = timezone.now()
    auth_record = AuthRecord(user=user, login_at=current_time,
                             expires_by=current_time + timedelta(hours=refresh_token_delta))
    auth_record.save()

    refresh_token_payload = {
        "user_id": user.id,
        "record_pk": auth_record.id,
        "iat": current_time,
        "type": "refresh_token",
    }

    # return jwt.encode(
    #     refresh_token_payload, settings.SECRET_KEY, algorithm="HS256").decode("utf-8")
    return jwt.encode(refresh_token_payload, settings.SECRET_KEY, algorithm="HS256")


def verify_jwt_token(request: HttpRequest) -> (bool, str, int):
    """[summary]
    """
    # get header
    flag = True
    message = ""
    user_id = ""
    header = request.META.get("HTTP_AUTHORIZATION")
    try:
        if header is None:
            raise jwt.InvalidTokenError

        auth_info = header.split(" ")
        if len(auth_info) != 2:
            raise jwt.InvalidTokenError
        auth_type, auth_token = auth_info

        if auth_type != "Bearer":
            raise jwt.InvalidTokenError
        token = jwt.decode(
            auth_token, settings.SECRET_KEY, algorithms="HS256")
        if token.get("type") != "access_token":
            raise jwt.InvalidTokenError
        user_id = token["user_id"]
    except jwt.ExpiredSignatureError:
        flag, message = False, "Token expired."
    except jwt.InvalidTokenError:
        flag, message = False, "Invalid token."
    return (flag, message, user_id)


@response_wrapper
@require_POST
def obtain_jwt_token(request: HttpRequest):
    """Handle requests which are to obtain jwt token

    [route]: /api/token-auth

    [method]: POST
    """
    data: dict = json.loads(request.body.decode())
    if not data:
        return failed_api_response(ErrorCode.INVALID_REQUEST_ARGS, "Invalid request args.")
    user = authenticate(username=data.get('username'), password=data.get('password'))
    if not user:
        return failed_api_response(ErrorCode.UNAUTHORIZED, "Login required.")
    return success_api_response({
        "access_token": generate_access_token(user.id),
        "refresh_token": generate_refresh_token(user)
    })


@response_wrapper
@require_GET
def refresh_jwt_token(request: HttpRequest):
    """Handle requests which are to refresh the expired tokens

    [route]: /api/token-refresh

    [method]: GET
    """
    try:
        header = request.META.get("HTTP_AUTHORIZATION")
        if header is None:
            raise jwt.InvalidTokenError

        auth_info = header.split(" ")
        if len(auth_info) != 2:
            raise jwt.InvalidTokenError
        auth_type, auth_token = auth_info

        if auth_type != "Bearer":
            raise jwt.InvalidTokenError
        token = jwt.decode(auth_token, settings.SECRET_KEY, algorithms="HS256")
        if token.get("type") != "refresh_token":
            raise jwt.InvalidTokenError
        auth_record = AuthRecord.objects.filter(
            pk=token.get("record_pk")).first()
        if auth_record is None:
            raise jwt.InvalidTokenError
        if auth_record and auth_record.expires_by < timezone.now():
            raise jwt.ExpiredSignatureError
        return success_api_response({"access_token": generate_access_token(token.get("user_id"))})
    except jwt.ExpiredSignatureError:
        return auth_failed("Token expired.")
    except jwt.InvalidTokenError:
        return auth_failed("Invalid token.")


def jwt_auth():
    """JWT authorization and permission control decorator for REST APIs
    """
    def decorator(func):
        def wrapper(request: HttpRequest, *args, **kwargs):
            (flag, message, user_id) = verify_jwt_token(request)
            if not flag:
                return auth_failed(message)
            request_user = User.objects.filter(pk=user_id).first()
            if request_user is None:
                return auth_failed("Sorry, your account has been disabled.")
            request.user = request_user
            # permission check
            return func(request, *args, **kwargs)
        return wrapper
    return decorator
