__all__ = [
    # APIs
    'get_login_info',
    'set_qq_profile',
    'qidian_get_account_info',
    '_get_model_show',
    '_set_model_show',
    'get_online_clients',
    'get_stranger_info',
    'get_friend_list',
    'get_unidirectional_friend_list',
    'delete_friend',
    'delete_unidirectional_friend',
    'send_private_msg',
    'send_group_msg',
    'send_msg',
    'get_msg',
    'delete_msg',
    'mark_msg_as_read',
    'get_forward_msg',
    'send_group_forward_msg',
    'send_private_forward_msg',
    'get_group_msg_history',
    'get_image',
    'can_send_image',
    'ocr_image',
    'get_record',
    'can_send_record',
    'set_friend_add_request',
    'set_group_add_request',
    'get_group_info',
    'get_group_list',
    'get_group_member_info',
    'get_group_member_list',
    'get_group_honor_info',
    'get_group_system_msg',
    'get_essence_msg_list',
    'get_group_at_all_remain',
    'set_group_name',
    'set_group_portrait',
    'set_group_admin',
    'set_group_card',
    'set_group_special_title',
    'set_group_ban',
    'set_group_whole_ban',
    'set_group_anonymous_ban',
    'set_essence_msg',
    'delete_essence_msg',
    'send_group_sign',
    'set_group_anonymous',
    '_send_group_notice',
    '_get_group_notice',
    'set_group_kick',
    'set_group_leave',
    'upload_group_file',
    'delete_group_file',
    'create_group_file_folder',
    'delete_group_folder',
    'get_group_file_system_info',
    'get_group_root_files',
    'get_group_files_by_folder',
    'get_group_file_url',
    'upload_private_file',
    'get_cookies',
    'get_csrf_token',
    'get_credentials',
    'get_version_info',
    'get_status',
    'set_restart',
    'clean_cache',
    'reload_event_filter',
    'download_file',
    '__get_word_slices',
    '__handle_quick_operation',
    # Types
    'UserId',
    'GroupId',
    'MessageId',
    'Message',
    'MessageEvent',
    # Regex patterns
    'AT_PATTERN',
    'REPLY_PATTERN',
    'SPECIAL_PATTERN',
    # Utils
    'custom_forward_node',
    'reference_forward_node',
    'session_id',
    'username',
    'groupname',
    'send_forward_msg',
    'send',
    'send_by'
]

from typing import cast, Optional

from nonebot.adapters.onebot.v11.event import MessageEvent

from .api import *
from .model import *


AT_PATTERN = r'\[CQ:at,qq=(\d+|all)\]'
REPLY_PATTERN = r'\[CQ:reply,id=(-?\d+)\]'
SPECIAL_PATTERN = r'\[CQ:(' + '|'.join([
    'record',   'video',    'rps',      'dice',     'shake',    'share',
    'contact',  'location', 'music',    'reply',    'redbag',   'poke',
    'gift',     'forward',  'node',     'xml',      'json',     'tts',
    'cardimage'
]) + r'),.*?\]|\[CQ:image,.*?type=(flash|show).*?\]]'


def session_id(event: MessageEvent) -> UserId | GroupId:
    return getattr(event, 'group_id', event.user_id)


async def username(
    user_id: UserId,
    group_id: Optional[GroupId] = None,
    no_cache: bool = False
) -> str:
    if group_id is not None:
        member = await get_group_member_info(group_id, user_id, no_cache)
        return member['card'] or member['nickname']
    return (await get_stranger_info(user_id, no_cache))['nickname']


async def groupname(group_id: GroupId, no_cache: bool = False) -> str:
    return (await get_group_info(group_id, no_cache))['group_name']


async def send_forward_msg(
    messages: list[ForwardNode],
    *,
    user_id: Optional[UserId] = None,
    group_id: Optional[GroupId] = None
) -> ForwardMessage:
    if user_id is None:
        assert group_id is not None
        return await send_group_forward_msg(group_id, messages)
    return await send_private_forward_msg(user_id, messages)


async def send(
    message: Message | list[ForwardNode],
    *,
    user_id: Optional[UserId] = None,
    group_id: Optional[GroupId] = None,
    auto_escape: bool = False
) -> MessageId:
    if type(message) == list:
        return (await send_forward_msg(
            messages=message,
            user_id=user_id,
            group_id=group_id
        ))['message_id']
    return await send_msg(
        message=cast(Message, message),
        auto_escape=auto_escape,
        user_id=user_id,
        group_id=group_id
    )


async def send_by(
    event: MessageEvent,
    message: Message | list[ForwardNode],
    auto_escape: bool = False
) -> MessageId:
    return await send(
        message,
        user_id=event.user_id,
        group_id=getattr(event, 'group_id', None),
        auto_escape=auto_escape
    )
