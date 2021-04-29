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
from core.api.notification import (NOTIFICATION_API, NOTIFICATION_SET_API)
from core.api.project import create_project, PROJECT_API, get_project_list
from core.api.recommend import recommend
from core.api.topic import (TOPIC_API, create_topic, get_topic_list)
from core.api.discussion import (create_discussion, delete_discussion, get_discussion, get_discussion_list)
from core.api.image import (IMAGE_API, IMAGE_SET_API)
from core.api.timeline import (TIMELINE_API, create_timeline, get_timeline_list)
from core.api.project_mk import (PROJECT_MK_API, create_project_mk, get_project_mk_list)
from core.api.word_cloud import word_cloud

from core.api.paper import create_paper, delete_paper, get_paper, PAPER_API, list_paper_page

urlpatterns = [

    # user apis
    path('token-auth', obtain_jwt_token),
    path('token-refresh', refresh_jwt_token),
    path('user/create', CREATE_USER_API),
    path('user/change-password', change_password),
    path('user/forget-password', FORGET_PASSWORD_API),
    path('user/profile', get_profile),
    path('user/icon', USER_ICON_API),

    # comment apis
    path('comment/create', create_comment),
    path('comment/delete', delete_comment),
    path('comment/<int:id>', get_comment),
    path('comment', get_comment_list),

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

    # paper apis
    path('paper', create_paper),
    path('paper/<int:id>', PAPER_API),
    path('paper/page/<int:pindex>', list_paper_page),

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
