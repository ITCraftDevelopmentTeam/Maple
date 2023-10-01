__all__ = [
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
    '__handle_quick_operation'
]

from datetime import timedelta
from typing import overload, cast, Any, Optional, Literal

from nonebot import get_bot

from .._sorcery import funcname
from .model import *


async def _call_api(api: Optional[str] = None, **data: Any) -> Any:
    if api is None:
        api = funcname(depth=1).replace('__', '.')
    resp = await get_bot().call_api(api, **{
        key: int(value) if key.endswith('_id') else value
        for key, value in data.items() if value is not None
    })
    if isinstance(resp, dict) and len(resp := cast(dict[Any, Any], resp)) == 1:
        resp = list(resp.values())[0]
    return resp


async def get_login_info() -> User:
    return await _call_api()


async def set_qq_profile(
    nickname: str,
    company: str,
    email: str,
    college: str,
    personal_note: str
) -> None:
    await _call_api(
        'set_qq_profile',
        nickname=nickname,
        company=company,
        email=email,
        college=college,
        personal_note=personal_note
    )


async def qidian_get_account_info() -> Any:
    return await _call_api()


async def _get_model_show(model: str) -> list[Variant]:
    return await _call_api(model=model)


async def _set_model_show(model: str, model_show: str) -> None:
    await _call_api(model=model, model_show=model_show)


async def get_online_clients(no_cache: bool) -> list[Device]:
    return await _call_api(no_cache=no_cache)


async def get_stranger_info(
    user_id: UserId,
    no_cache: bool = False
) -> Stranger:
    return await _call_api(user_id=user_id, no_cache=no_cache)


async def get_friend_list() -> list[Friend]:
    return await _call_api()


async def get_unidirectional_friend_list() -> list[UnidirectionalFriend]:
    return await _call_api()


async def delete_friend(user_id: UserId) -> None:
    await _call_api(user_id=user_id)


async def delete_unidirectional_friend(user_id: UserId) -> None:
    await _call_api(user_id=user_id)


async def send_private_msg(
    message: Message,
    user_id: UserId,
    group_id: Optional[GroupId] = None,
    *, auto_escape: bool = False
) -> MessageId:
    return await _call_api(
        message=message,
        user_id=user_id,
        group_id=group_id,
        auto_escape=auto_escape
    )


async def send_group_msg(
    message: Message,
    group_id: Optional[GroupId] = None,
    *,
    auto_escape: bool = False
) -> MessageId:
    return await _call_api(
        message=message,
        group_id=group_id,
        auto_escape=auto_escape
    )


async def send_msg(
    message: Message,
    *,
    user_id: Optional[UserId] = None,
    group_id: Optional[GroupId] = None,
    auto_escape: bool = False,
) -> MessageId:
    assert user_id or group_id
    return await _call_api(
        message=message,
        user_id=user_id,
        group_id=group_id,
        auto_escape=auto_escape
    )


async def get_msg(message_id: MessageId) -> PrivateMessage | GroupMessage:
    return await _call_api(message_id=message_id)


async def delete_msg(message_id: MessageId) -> None:
    await _call_api(message_id=message_id)


async def mark_msg_as_read(
    message_id: MessageId
) -> None:
    await _call_api(message_id=message_id)


async def get_forward_msg(message_id: MessageId) -> list[ForwardNodeInfo]:
    return await _call_api(message_id=message_id)


async def send_group_forward_msg(
    group_id: GroupId,
    messages: list[ForwardNode]
) -> ForwardMessage:
    return await _call_api(group_id=group_id, messages=messages)


async def send_private_forward_msg(
    user_id: UserId,
    messages: list[ForwardNode]
) -> ForwardMessage:
    return await _call_api(user_id=user_id, messages=messages)


async def get_group_msg_history(
    group_id: GroupId,
    message_seq: Optional[int] = None
) -> list[Message]:
    return await _call_api(group_id=group_id, message_seq=message_seq)


async def get_image(file: str) -> Image:
    return await _call_api(file=file)


async def can_send_image() -> bool:
    return await _call_api()


async def ocr_image(image: str) -> OCR:
    return await _call_api(image=image)


async def get_record(file: str, out_format: RecordFormat) -> str:
    raise NotImplementedError()
    return await _call_api(file=file, out_format=out_format)


async def can_send_record() -> bool:
    return await _call_api()


async def set_friend_add_request(
    flag: str,
    approve: bool = True,
    remark: Optional[str] = None
) -> None:
    await _call_api(flag=flag, approve=approve, remark=remark)


async def set_group_add_request(
    flag: str,
    sub_type: Literal['add', 'invite'],
    approve: bool = True,
    reason: Optional[str] = None
) -> None:
    await _call_api(flag=flag, type=sub_type, approve=approve, reason=reason)


async def get_group_info(
        group_id: GroupId,
        no_cache: bool = False
) -> GroupInfo:
    return await _call_api(group_id=group_id, no_cache=no_cache)


async def get_group_list(no_cache: bool = False) -> list[GroupInfo]:
    return await _call_api(no_cache=no_cache)


async def get_group_member_info(
    group_id: GroupId,
    user_id: UserId,
    no_cache: bool = False
) -> RichGroupMember:
    return await _call_api(
        group_id=group_id,
        user_id=user_id,
        no_cache=no_cache
    )


async def get_group_member_list(
    group_id: GroupId,
    no_cache: bool = False
) -> list[GroupMember]:
    return await _call_api(group_id=group_id, no_cache=no_cache)


@overload
async def get_group_honor_info(
    group_id: GroupId,
    type: HonorType
) -> list[Honored]: ...


@overload
async def get_group_honor_info(
    group_id: GroupId,
    type: Literal['current_talkative']
) -> CurrentTalkative: ...


@overload
async def get_group_honor_info(
    group_id: GroupId,
    type: Literal['all']
) -> AllHonors: ...


async def get_group_honor_info(
    group_id: GroupId,
    type: HonorType | Literal['current_talkative', 'all']
) -> list[Honored] | CurrentTalkative | AllHonors:
    resp = await _call_api(
        group_id=group_id,
        type=type.removeprefix('current_')
    )
    match type:
        case 'all':
            return resp
        case 'current_talkative':
            return resp['current_talkative']
        case honor:
            return resp[f'{honor}_list']


async def get_group_system_msg() -> GroupSystemMessage:
    return await _call_api()


async def get_essence_msg_list(group_id: GroupId) -> list[EssenceMessage]:
    return await _call_api(group_id=group_id)


async def get_group_at_all_remain(group_id: GroupId) -> GroupAtAllRemain:
    return await _call_api(group_id=group_id)


async def set_group_name(group_id: GroupId, group_name: str) -> None:
    await _call_api(group_id=group_id, group_name=group_name)


async def set_group_portrait(
    group_id: GroupId,
    file: str,
    cache: bool = True
) -> None:
    await _call_api(group_id=group_id, file=file, cache=int(cache))


async def set_group_admin(
    group_id: GroupId,
    user_id: UserId,
    enable: bool = True
) -> None:
    await _call_api(group_id=group_id, user_id=user_id, enable=enable)


async def set_group_card(
    group_id: GroupId,
    user_id: UserId,
    card: Optional[str] = None
) -> None:
    await _call_api(group_id=group_id, user_id=user_id, card=card)


async def set_group_special_title(
    group_id: GroupId,
    user_id: UserId,
    special_title: Optional[str] = None,
    duration: int | timedelta = -1
) -> None:
    if isinstance(duration, timedelta):
        duration = int(duration.total_seconds())
    await _call_api(
        group_id=group_id,
        user_id=user_id,
        special_title=special_title,
        duration=duration
    )


async def set_group_ban(
    group_id: GroupId,
    user_id: UserId,
    duration: int | timedelta = 30 * 60
) -> None:
    if isinstance(duration, timedelta):
        duration = int(duration.total_seconds())
    await _call_api(
        group_id=group_id,
        user_id=user_id,
        duration=duration
    )


async def set_group_whole_ban(group_id: GroupId, enable: bool = True) -> None:
    await _call_api(group_id=group_id, enable=enable)


async def set_group_anonymous_ban(
    group_id: GroupId,
    anonymous: Optional[Anonymous] = None,
    anonymous_flag: Optional[str] = None,
    duration: int | timedelta = 30 * 60
) -> None:
    assert anonymous or anonymous_flag
    if isinstance(duration, timedelta):
        duration = int(duration.total_seconds())
    await _call_api(
        group_id=group_id,
        anonymous=anonymous,
        anonymous_flag=anonymous_flag,
        duration=duration
    )


async def set_essence_msg(message_id: MessageId) -> None:
    await _call_api(message_id=message_id)


async def delete_essence_msg(message_id: MessageId) -> None:
    await _call_api(message_id=message_id)


async def send_group_sign(group_id: GroupId) -> None:
    await _call_api(group_id=group_id)


async def set_group_anonymous(group_id: GroupId, enable: bool = True) -> None:
    await _call_api(group_id=group_id, enable=enable)


async def _send_group_notice(
    group_id: GroupId,
    content: str,
    image: Optional[str] = None
) -> None:
    await _call_api(group_id=group_id, content=content, image=image)


async def _get_group_notice(group_id: GroupId) -> list[GroupNotice]:
    return await _call_api(group_id=group_id)


async def set_group_kick(
    group_id: GroupId,
    user_id: UserId,
    reject_add_request: bool = False
) -> None:
    await _call_api(
        group_id=group_id,
        user_id=user_id,
        reject_add_request=reject_add_request
    )


async def set_group_leave(group_id: GroupId, is_dismiss: bool = False) -> None:
    await _call_api(group_id=group_id, is_dismiss=is_dismiss)


async def upload_group_file(
    group_id: GroupId,
    file: str,
    name: str,
    folder: Optional[str] = None
) -> None:
    await _call_api(group_id=group_id, file=file, name=name, folder=folder)


async def delete_group_file(
    group_id: GroupId,
    file_id: str,
    busid: int
) -> None:
    await _call_api(group_id=group_id, file_id=file_id, busid=busid)


async def create_group_file_folder(
    group_id: GroupId,
    name: str,
    parent_id: str = '/'
) -> None:
    assert parent_id == '/'
    await _call_api(group_id=group_id, name=name, parent_id=parent_id)


async def delete_group_folder(group_id: GroupId, folder_id: str) -> None:
    await _call_api(group_id=group_id, folder_id=folder_id)


async def get_group_file_system_info(group_id: GroupId) -> GroupFileSystemInfo:
    return await _call_api(group_id=group_id)


async def get_group_root_files(group_id: GroupId) -> GroupFolderInfo:
    return await _call_api(group_id=group_id)


async def get_group_files_by_folder(
    group_id: GroupId,
    folder_id: str
) -> GroupFolderInfo:
    return await _call_api(group_id=group_id, folder_id=folder_id)


async def get_group_file_url(
    group_id: GroupId,
    file_id: str,
    busid: int
) -> str:
    return await _call_api(group_id=group_id, file_id=file_id, busid=busid)


async def upload_private_file(user_id: UserId, file: str, name: str) -> None:
    await _call_api(user_id=user_id, file=file, name=name)


async def get_cookies(domain: Optional[str] = None) -> str:
    raise NotImplementedError()
    return await _call_api(domain=domain)


async def get_csrf_token() -> int:
    raise NotImplementedError()
    return await _call_api()


async def get_credentials(domain: Optional[str] = None) -> Credentials:
    raise NotImplementedError()
    return await _call_api(domain=domain)


async def get_version_info() -> VersionInfo:
    return await _call_api()


async def get_status() -> Status:
    return await _call_api()


async def set_restart(delay: int | timedelta) -> Status:
    raise NotImplementedError()
    if isinstance(delay, timedelta):
        delay = int(delay.total_seconds() * 1000)
    return await _call_api(delay=delay)


async def clean_cache() -> None:
    raise NotImplementedError()
    await _call_api()


async def reload_event_filter(file: str) -> None:
    await _call_api(file=file)


async def download_file(
    url: str,
    thread_count: int,
    headers: str | list[str]
) -> str:
    return await _call_api(url=url, thread_count=thread_count, headers=headers)


async def __get_word_slices(content: str) -> list[str]:
    return await _call_api(content=content)


async def __handle_quick_operation(
    content: dict[str, Any],
    operation: dict[str, Any]
) -> None:
    return await _call_api(content=content, operation=operation)
