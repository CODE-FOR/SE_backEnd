"""
define the url routes of core api
"""
from django.urls import path
from core.api.auth import obtain_jwt_token, refresh_jwt_token
from core.api.my_post import list_posts
from core.api.profile import get_profile
from core.api.sign_up import change_password, CREATE_USER_API, FORGET_PASSWORD_API
from core.api.comment import create_comment, delete_comment, get_comment, get_comment_list
from core.api.micro_knowledge import (favor, unfavor, like_micro_knowledge, FAVORITES_SET_API, MICRO_KNOWLEDGE_SET_API)
from core.api.judge import MICRO_KNOWLEDGE_JUDGE_API
from core.api.user import follow, unfollow, list_follower_recent
from core.api.micro_evidence import (create_micro_evidence,
                                     MICRO_EVIDENCE_API, MICRO_EVIDENCE_SET_API)
from core.api.micro_conjecture import (create_micro_conjecture,
                                       MICRO_CONJECTURE_API, MICRO_CONJECTURE_SET_API)
from core.api.tag import TAG_SET_API

from core.api.fan import list_fans
from core.api.follower import list_followers
from core.api.user_icon import USER_ICON_API
from core.api.user_icon import get_icon_by_id
from core.api.notification import (NOTIFICATION_API, NOTIFICATION_SET_API)
from core.api.project import create_project, PROJECT_API, get_project_list
from core.api.recommend import recommend
from core.api.topic import (TOPIC_API, create_topic, get_topic_list)
from core.api.discussion import (create_discussion, delete_discussion, get_discussion, get_discussion_list)
from core.api.image import (IMAGE_API, IMAGE_SET_API)
from core.api.timeline import (TIMELINE_API, create_timeline, get_timeline_list)
from core.api.project_mk import (PROJECT_MK_API, create_project_mk, get_project_mk_list)
from core.api.word_cloud import word_cloud

from core.api.paper import create_paper, PAPER_API, list_paper_page, get_paper_title, \
    like_paper, collect_paper, report_paper, list_paper_report, delete_paper
from core.api.interpretation import create_interpretation, INTERPRETATION_API, \
    list_interpretation_page, like_interpretation, collect_interpretation, delete_interpretation, \
    report_interpretation, list_interpretation_report
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
    path('user/icon', USER_ICON_API),
    path('user/icon-by-id', get_icon_by_id),

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

    # micro knowledge apis
    path('micro-knowledge/<int:eid>/favor', favor),
    path('micro-knowledge/<int:eid>/unfavor', unfavor),
    path('micro-knowledge/<int:id>/like', like_micro_knowledge),
    path('micro-knowledge/page/<int:pindex>', MICRO_KNOWLEDGE_SET_API),
    path('favorites/page/<int:pindex>', FAVORITES_SET_API),
    path('micro-knowledge/<int:id>/judge', MICRO_KNOWLEDGE_JUDGE_API),

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

    # interpretation apis
    path('interpretation/create', create_interpretation),
    path('interpretation/<int:id>', INTERPRETATION_API),
    path('interpretation/page/<int:pindex>', list_interpretation_page),
    path('interpretation/<int:id>/like', like_interpretation),
    path('interpretation/<int:id>/collect', collect_interpretation),
    path('interpretation/delete', delete_interpretation),

    path('interpretation/report/create', report_interpretation),
    path('interpretation/report/page/<int:pindex>', list_interpretation_report),

    # search apis
    path('search/page/<int:pindex>', search_by_tag),

    # micro evidence apis
    path('micro-evidence', create_micro_evidence),
    path('micro-evidence/<int:id>', MICRO_EVIDENCE_API),
    path('micro-evidence/page/<int:pindex>', MICRO_EVIDENCE_SET_API),

    # micro conjecture apis
    path('micro-conjecture', create_micro_conjecture),
    path('micro-conjecture/<int:id>', MICRO_CONJECTURE_API),
    path('micro-conjecture/page/<int:pindex>', MICRO_CONJECTURE_SET_API),

    # tag apis
    path('tags/page/<int:pindex>', TAG_SET_API),

    # list posts
    path('post/<int:uid>', list_posts),

    # list fans
    path('fan/<int:uid>', list_fans),

    # list follower
    path('follower/<int:uid>', list_followers),

    # notifications
    path('notification', NOTIFICATION_API),
    path('notification/page/<int:pindex>', NOTIFICATION_SET_API),

    # project
    path('project/create', create_project),
    path('project/<int:id>', PROJECT_API),
    path('project', get_project_list),

    # topic
    path('topic/create', create_topic),
    path('topic/<int:id>', TOPIC_API),
    path('topic', get_topic_list),

    # discussion
    path('discussion/create', create_discussion),
    path('discussion/delete', delete_discussion),
    path('discussion/<int:id>', get_discussion),
    path('discussion', get_discussion_list),

    ##timeline
    # path('timeline/create', create_timeline),
    # path('timeline/<int:id>', TIMELINE_API),
    # path('timeline', get_timeline_list),

    # project mk
    path('project/micro-knowledge/create', create_project_mk),
    path('project/micro-knowledge/<int:id>', PROJECT_MK_API),
    path('project/micro-knowledge', get_project_mk_list),

    # test
    path('recommend', recommend),

    # images
    path('image', IMAGE_API),
    path('image/page/<pindex: int>', IMAGE_SET_API),

    # word cloud
    path('cloud', word_cloud),
]
