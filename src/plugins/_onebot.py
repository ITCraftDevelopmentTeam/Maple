from typing import Optional

from nonebot import get_bot
from nonebot.adapters import Message, MessageSegment, MessageTemplate
from nonebot.adapters.onebot.v11.event import MessageEvent, GroupMessageEvent
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
    "gift",     "forward",  "node",     "xml",      "json",     "cardimage",
    "tts"
]) + r"),.*?\]|\[CQ:image,.*?type=(flash|send).*?\]]"


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
    message: AnyMessage,
    auto_escape: bool = False,
    group_id: Optional[GroupID] = None,
    user_id: Optional[UserID] = None
) -> MessageID:
    kwargs = {}
    if group_id is not None:
        kwargs["group_id"] = int(group_id)
    elif user_id is not None:
        kwargs["user_id"] = int(user_id)

    return (await get_bot().send_msg(
        message=message,
        auto_escape=auto_escape,
        **kwargs
    ))["message_id"]


async def send(
    event:  MessageEvent,
    message: AnyMessage,
    auto_escape: bool = False
) -> MessageID:
    if isinstance(event, GroupMessageEvent):
        kwargs = {"group_id": event.group_id}
    else:
        kwargs = {"user_id": event.user_id}

    return await send_msg(
        message=message,
        auto_escape=auto_escape,
        **kwargs
    )


def get_event_id(event: MessageEvent) -> UserID | GroupID:
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
    user_id: UserID,
    content: AnyMessage | list[ForwardNode],
    name: Optional[str] = None,
    group_id: Optional[GroupID] = None,
    time: Optional[int | str] = None
) -> ForwardNode:
    if name is None:
        name = await get_user_name(user_id, group_id)
    node: ForwardNode = {
        "type": "node",
        "data": {
            "name": name,
            "uin": str(user_id),
            "content": content
        }
    }
    if time is not None:
        node["data"]["time"] = int(time)
    return node


def referencing_forward_node(id: MessageID) -> ForwardNode:
    return {
        "type": "node",
        "data": {
            "id": str(id)
        }
    }


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
    if user_id is not None:
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
