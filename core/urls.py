"""
define the url routes of core api
"""
from django.urls import path
from core.api.auth import obtain_jwt_token, refresh_jwt_token

from core.api.profile import get_profile
from core.api.sign_up import change_password, CREATE_USER_API, FORGET_PASSWORD_API
from core.api.comment import create_comment, delete_comment, get_comment, get_comment_list

from core.api.user import follow, unfollow, list_follower_recent

from core.api.tag import TAG_SET_API

from core.api.fan import list_fans
from core.api.follower import list_followers

from core.api.notification import (NOTIFICATION_API, NOTIFICATION_SET_API, NOTIFICATION_NUM_API)

from core.api.image import (IMAGE_API, IMAGE_SET_API)


from core.api.paper import create_paper, PAPER_API, list_paper_page, get_paper_title, \
    like_paper, collect_paper, report_paper, list_paper_report, delete_paper, cancel_report_paper
from core.api.interpretation import create_interpretation, INTERPRETATION_API, \
    list_interpretation_page, like_interpretation, collect_interpretation, delete_interpretation, \
    report_interpretation, list_interpretation_report, recommend_inter, cancel_report_interpretation
from core.api.search import search_by_tag

from core.api.post import follow_recent, get_post_by_id, get_collect_by_id

from core.api.chat import get_user_chat_by_id, clear_unread_by_id, get_chat_list, add_user_into_list, \
    get_message_list_by_id, get_message_by_id

from core.api.user import ban, unban, list_user_all, list_ban_all

urlpatterns = [

    # user apis
    path('token-auth', obtain_jwt_token),
    path('token-refresh', refresh_jwt_token),
    path('user/create', CREATE_USER_API),
    path('user/change-password', change_password),
    path('user/forget-password', FORGET_PASSWORD_API),
    path('user/profile', get_profile),

    # user post apis
    path('recent/page/<int:pindex>', follow_recent),
    path('post/<int:uid>', get_post_by_id),
    path('favorites/<int:uid>', get_collect_by_id),

    # comment apis
    path('comment/create', create_comment),
    path('comment/delete', delete_comment),
    path('comment/<int:id>', get_comment),
    path('comment', get_comment_list),

    # manage apis
    path('ban/manage', ban),
    path('unban/manage', unban),
    path('ban-list/<int:pindex>', list_ban_all),
    path('user-list/<int:pindex>', list_user_all),

    # user apis
    path('user/<int:pid>/follow', follow),
    path('user/<int:pid>/unfollow', unfollow),
    path('recent/page/<int:pindex>', list_follower_recent),

    # chat apis
    path('chat-user-list', get_chat_list),
    path('clear-unread', clear_unread_by_id),
    path('chat-user', get_user_chat_by_id),
    path('add-usr-into-chat-list', add_user_into_list),
    path('chat-message-list', get_message_list_by_id),
    path('chat-message', get_message_by_id),

    # paper apis
    path('paper', create_paper),
    path('paper/<int:id>', PAPER_API),
    path('paper/page/<int:pindex>', list_paper_page),
    path('paper/titles', get_paper_title),
    path('paper/<int:id>/like', like_paper),
    path('paper/<int:id>/collect', collect_paper),

    path('paper/report/create', report_paper),
    path('paper/report/page/<int:pindex>', list_paper_report),
    path('paper/delete', delete_paper),
    path('paper/report/cancel', cancel_report_paper),

    # interpretation apis
    path('interpretation/create', create_interpretation),
    path('interpretation/<int:id>', INTERPRETATION_API),
    path('interpretation/page/<int:pindex>', list_interpretation_page),
    path('interpretation/<int:id>/like', like_interpretation),
    path('interpretation/<int:id>/collect', collect_interpretation),
    path('interpretation/delete', delete_interpretation),

    path('interpretation/report/create', report_interpretation),
    path('interpretation/report/page/<int:pindex>', list_interpretation_report),
    path('interpretation/report/cancel', cancel_report_interpretation),

    # search apis
    path('search/page/<int:pindex>', search_by_tag),

    # tag apis
    path('tags/page/<int:pindex>', TAG_SET_API),

    # list fans
    path('fan/<int:uid>', list_fans),

    # list follower
    path('follower/<int:uid>', list_followers),

    # notifications
    path('notification', NOTIFICATION_API),
    path('notification/num', NOTIFICATION_NUM_API),
    path('notification/page/<int:pindex>', NOTIFICATION_SET_API),

    # timeline
    # path('timeline/create', create_timeline),
    # path('timeline/<int:id>', TIMELINE_API),
    # path('timeline', get_timeline_list),

    # test
    # path('recommend', recommend),
    path('recommend', recommend_inter),

    # images
    path('image', IMAGE_API),
    path('image/page/<pindex: int>', IMAGE_SET_API),
]
