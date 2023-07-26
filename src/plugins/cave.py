import re
from random import choice
from functools import partial
from typing import Optional

from nonebot import CommandGroup
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, MessageEvent, escape


from ._lang import text, LangType
from ._store import JsonDict
from ._onebot import (
    UserID, GroupID,
    send_msg, get_msg, get_user_name,
    REPLY_PATTERN, SPECIAL_PATTERN
)


caves = JsonDict("caves.json", dict[str, dict])
cave = CommandGroup("cave", aliases={"cav"})


@cave.command(tuple()).handle()
async def cave_handle(event: MessageEvent) -> None:
    await read_cave(
        cave_id=choice(list(caves.keys())),
        lang=event,
        user_id=event.user_id,
        group_id=getattr(event, "group_id", None)
    )


@cave.command("add").handle()
async def cave_handle(
    matcher: Matcher,
    event: MessageEvent,
    arg: Message = CommandArg()
) -> None:
    if match := re.match(REPLY_PATTERN, event.raw_message):
        data = await get_msg(match.group()[13:-1])
        content = data["message"]
        sender = data["sender"]["user_id"]
    else:
        content = str(arg).strip()
        sender = event.user_id
    cave_id = 0
    while str(cave_id) in caves.keys():
        cave_id += 1
    cave_id = str(cave_id)
    caves[cave_id] = {"content": content, "sender": sender}
    await matcher.send(text(event, "cave.add", cave_id=cave_id))


@cave.command("get").handle()
async def cave_handle(
    event: MessageEvent,
    arg: Message = CommandArg()
) -> None:
    await read_cave(
        cave_id=str(arg).strip(),
        lang=event,
        user_id=event.user_id,
        group_id=getattr(event, "group_id", None)
    )


async def read_cave(
    cave_id: str,
    lang: LangType,
    group_id: Optional[GroupID] = None,
    user_id: Optional[UserID] = None
) -> None:
    caves = JsonDict("caves.json", dict)
    send = partial(send_msg, user_id=user_id, group_id=group_id)
    if cave_id in caves.keys():
        message = caves[cave_id]
        sender = message["sender"]
        content = message["content"]
        if isinstance(sender, int):
            sender = await get_user_name(sender, group_id)
        sender = escape(sender)
        if re.match(SPECIAL_PATTERN, content):
            await send(Message(text(
                lang, "cave.title",
                cave_id=cave_id,
                sender=sender
            )))
            await send(Message(content))
        else:
            await send(Message(text(
                lang, "cave.read",
                cave_id=cave_id,
                content=content,
                sender=sender
            )))
    else:
        await send(text(lang, "cave.non-exist", cave_id=cave_id))
