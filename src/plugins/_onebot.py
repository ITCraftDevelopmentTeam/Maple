import re
from typing import Optional

from nonebot import get_bot
from nonebot.adapters import Message, MessageSegment, MessageTemplate
from nonebot.adapters.onebot.v11.event import MessageEvent
from nonebot.adapters.onebot.v11.exception import ActionFailed

UserID = GroupID = MessageID = str | int
AnyMessage = str | Message | MessageSegment | MessageTemplate
MessageType = dict[str, int | str | dict[str, int | str]]
ForwardNode = dict[str, str |
                   dict[str, str | int | AnyMessage | list["ForwardNode"]]]

AT_PATTERN = r"\[CQ:at,qq=(\d+|all)\]"
REPLY_PATTERN = r"\[CQ:reply,id=(-?\d+)\]"
SPECIAL_PATTERN = r"\[CQ:(" + "|".join([
    "record",   "video",    "rps",      "dice",     "shake",    "share",
    "contact",  "location", "music",    "reply",    "redbag",   "poke",
    "gift",     "forward",  "node",     "xml",      "json",     "tts",
    "cardimage"
]) + r"),.*?\]|\[CQ:image,.*?type=(flash|show).*?\]]"


async def send_group_msg(
    group_id: GroupID,
    message: AnyMessage,
    auto_escape: bool = False
) -> MessageID:
    return (await get_bot().send_group_msg(
        group_id=int(group_id),
        message=message,
        auto_escape=auto_escape
    ))["message_id"]


async def send_private_msg(
    user_id: UserID,
    message: AnyMessage,
    group_id: Optional[GroupID] = None,
    auto_escape: bool = False
) -> MessageID:
    return (await get_bot().send_private_msg(
        message=message,
        user_id=int(user_id),
        group_id=int(group_id),
        auto_escape=auto_escape
    ))["message_id"]


async def send_msg(
    message: AnyMessage | list[ForwardNode],
    user_id: Optional[UserID] = None,
    group_id: Optional[GroupID] = None,
    auto_escape: bool = False
) -> MessageID:
    if group_id is not None:
        return (await get_bot().send_msg(
            message=message,
            auto_escape=auto_escape,
            group_id=group_id
        ))["message_id"]
    assert user_id is not None
    return (await get_bot().send_msg(
        message=message,
        auto_escape=auto_escape,
        user_id=user_id
    ))["message_id"]


async def send(
    event:  MessageEvent,
    message: AnyMessage | list[ForwardNode],
    auto_escape: bool = False
) -> MessageID:
    user_id = event.user_id
    group_id = getattr(event, "group_id", None)
    if type(message) == list:
        return await send_forward_msg(
            messages=message,
            user_id=user_id,
            group_id=group_id
        )
    return await send_msg(
        message=message,
        auto_escape=auto_escape,
        user_id=user_id,
        group_id=group_id
    )


def get_session_id(event: MessageEvent) -> UserID | GroupID:
    return getattr(event, "group_id", event.user_id)


async def delete_msg(message_id: MessageID) -> None:
    await get_bot().delete_msg(message_id=int(message_id))


async def get_group_info(
    group_id: GroupID,
    no_cache: bool = False
) -> dict[str, str | int]:
    return await get_bot().get_group_info(
        group_id=int(group_id),
        no_cache=no_cache
    )


async def get_group_member_info(
    group_id: GroupID,
    user_id: UserID,
    no_cache: bool = False
) -> dict[str, str]:
    return await get_bot().get_group_member_info(
        group_id=int(group_id),
        user_id=int(user_id),
        no_cache=no_cache
    )


async def get_stranger_info(
    user_id: UserID,
    no_cache: bool = False
) -> dict[str, str]:
    return await get_bot().get_stranger_info(
        user_id=int(user_id),
        no_cache=no_cache
    )


async def custom_forward_node(
    content: AnyMessage | list[ForwardNode],
    user_id: UserID,
    group_id: Optional[GroupID] = None,
    name: Optional[str] = None,
    time: Optional[int] = None
) -> ForwardNode:
    if name is None:
        name = await get_user_name(user_id, group_id)
    node: ForwardNode = {"type": "node", "data": {
        "name": name,
        "uin": str(user_id),
        "content": content
    }}
    if time is not None:
        node["data"]["time"] = time
    return node


def referencing_forward_node(id: MessageID) -> ForwardNode:
    return {"type": "node", "data": {"id": str(id)}}


async def send_group_forward_msg(
    group_id: GroupID,
    messages: list[ForwardNode]
) -> None:
    await get_bot().send_group_forward_msg(
        group_id=int(group_id),
        messages=messages
    )


async def send_private_forward_msg(
    user_id: UserID,
    messages: list[ForwardNode]
) -> dict[str, int | str]:
    return await get_bot().send_private_forward_msg(
        user_id=int(user_id),
        messages=messages
    )


async def send_group_forward_msg(
    group_id: GroupID,
    messages: list[ForwardNode]
) -> dict[str, int | str]:
    await get_bot().send_group_forward_msg(
        group_id=int(group_id),
        messages=messages
    )


async def send_forward_msg(
    messages: list[ForwardNode],
    user_id: Optional[UserID] = None,
    group_id: Optional[GroupID] = None
) -> dict[str, int | str]:
    if group_id is not None:
        return await send_group_forward_msg(group_id, messages)
    assert user_id is not None
    return await send_private_forward_msg(user_id, messages)


async def get_group_msg_history(
    group_id: GroupID,
    message_seq: Optional[MessageID] = None
) -> list[MessageType]:
    return (await get_bot().get_group_msg_history(
        message_seq=message_seq,
        group_id=int(group_id)
    ))["messages"]


async def get_user_name(
    user_id: UserID,
    group_id: Optional[GroupID] = None,
    no_cache: bool = False
) -> str:
    if group_id is not None:
        try:
            info = await get_group_member_info(group_id, user_id, no_cache)
            return info["card"] or info["nickname"]
        except ActionFailed:
            pass
    return (await get_stranger_info(int(user_id), no_cache))["nickname"]


async def get_group_name(group_id: GroupID) -> str:
    try:
        return (await get_group_info(group_id))["group_name"]
    except ActionFailed:
        return str(group_id)


async def get_msg(
    message_id: MessageID
) -> dict[str, str | int | dict[str, str | int]]:
    return await get_bot().get_msg(message_id=int(message_id))


async def get_target_ids(raw_message: str) -> set[str]:
    if hasattr(raw_message, "raw_message"):
        raw_message = raw_message.raw_message
    target_ids = set(re.findall(AT_PATTERN, raw_message))
    if (match := re.match(REPLY_PATTERN, raw_message)):
        target_ids.add(str((await get_msg(match.group()[13:-1]))
                           ["sender"]["user_id"]))
    return {"all"} if "all" in target_ids else target_ids
