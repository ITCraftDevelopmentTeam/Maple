import re
from functools import partial
from random import choice
from pathlib import Path
from typing import cast

from nonebot import get_bot
from nonebot import CommandGroup
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, MessageEvent, escape

from ._lang import text
from ._onebot import (
    ForwardNode,
    send, get_msg, get_user_name, custom_forward_node, get_session_id,
    REPLY_PATTERN, SPECIAL_PATTERN
)
from ._store import JsonDict


text = partial(text, prefix="cave")
cave = CommandGroup("cave", aliases={"cav"})
branchs = JsonDict("cave.branchs.json", lambda: "session")


@cave.command(tuple()).handle()
async def cave_handle(matcher: Matcher, event: MessageEvent) -> None:
    branch_name, branch = get_branch(event)
    _text = partial(text, branch=branch_name)
    if not branch:
        await matcher.finish(_text(event, ".empty"))
    await send_cave(choice(list(branch.keys())), event)


@cave.command("add").handle()
async def cave_add_handle(
    matcher: Matcher,
    event: MessageEvent,
    arg: Message = CommandArg()
) -> None:
    branch_name, branch = get_branch(event)
    _text = partial(text, branch=branch_name)
    if founds := re.findall(REPLY_PATTERN, event.raw_message):
        data = await get_msg(founds[0])
        content = data["message"]
        user_id = data["sender"]["user_id"]
    else:
        content = str(arg).strip()
        user_id = event.user_id
    cave_id = 0
    while str(cave_id) in branch.keys():
        cave_id += 1
    cave_id = str(cave_id)
    branch[cave_id] = {"content": content, "user_id": user_id}
    await matcher.send(_text(event, ".cave.add", cave_id=cave_id))


@cave.command("get").handle()
async def cave_get_handle(
    matcher: Matcher,
    event: MessageEvent,
    arg: Message = CommandArg()
) -> None:
    branch_name, branch = get_branch(event)
    _text = partial(text, branch=branch_name)
    if not branch:
        await matcher.finish(_text(event, ".empty"))
    cave_id = str(arg).strip()
    if "-" in cave_id and str(event.user_id) in get_bot().config.superusers:
        start, end, *_ = cave_id.split("-")
        if not (start.isdecimal() and end.isdecimal()):
            await matcher.finish(_text(event, ".cave.non-exist", cave_id))
        await send(event, [
            await custom_forward_node(
                user_id=(user_id := branch[cave_id]["user_id"]),
                group_id=(group_id := getattr(event, "group_id", None)),
                content=[
                    await custom_forward_node(
                        content=message,
                        user_id=user_id,
                        group_id=group_id,
                        name=await get_user_name(user_id, group_id)
                    )
                    for message in await get_cave(cave_id, event)
                ],
                name=await get_user_name(user_id, group_id)
            )
            for cave_id in map(str, range(int(start), int(end) + 1))
            if cave_id in branch.keys()
        ])
        await matcher.finish()
    await send_cave(cave_id, event)


@cave.command("comment", aliases={"cmt"}).handle()
async def cave_comment_handle(
    matcher: Matcher,
    event: MessageEvent,
    arg: Message = CommandArg()
) -> None:
    cave_id, content = str(arg).strip().split(maxsplit=1)
    branch_name, branch = get_branch(event)
    _text = partial(text, branch=branch_name)
    if cave_id not in branch.keys():
        await matcher.finish(_text(event, ".cave.non-exist", cave_id=cave_id))
    if "comments" not in branch[cave_id].keys():
        branch[cave_id]["comments"] = {}
    comment_id = len(branch[cave_id]["comments"])
    branch[cave_id]["comments"][comment_id] = {
        "user_id": event.user_id,
        "content": content,
        "time": event.time
    }
    await matcher.send(_text(
        event, ".comment.add",
        cave_id=cave_id,
        comment_id=comment_id
    ))


@cave.command("remove", aliases={"rm"}).handle()
async def cave_remove_handle(
    matcher: Matcher,
    event: MessageEvent,
    arg: Message = CommandArg()
) -> None:
    comment_id = ""
    if " " in (cave_id := str(arg).strip()):
        cave_id, comment_id, *_ = cave_id.split()
    branch_name, branch = get_branch(event)
    _text = partial(text, branch=branch_name)
    if cave_id not in branch.keys():
        await matcher.finish(_text(event, ".cave.non-exist", cave_id=cave_id))
    if comment_id != "":    # remove comment
        comments = branch[cave_id].get("comments", {})
        if comment_id not in comments.keys():
            await matcher.finish(_text(
                event, ".comment.non-exist",
                cave_id=cave_id,
                comment_id=comment_id
            ))
        if (str(event.user_id) in get_bot().config.superusers
                or event.user_id == comments[comment_id]["user_id"]):
            branch.pop(cave_id)
            await matcher.finish(_text(
                event, ".comment.remove",
                cave_id=cave_id,
                comment_id=comment_id
            ))
        await matcher.send(_text(
            event, ".comment.remove.no-permission",
            cave_id=cave_id,
            comment_id=comment_id
        ))
    else:                   # remove cave
        if (str(event.user_id) in get_bot().config.superusers
                or event.user_id == branch[cave_id]["user_id"]):
            branch.pop(cave_id)
            await matcher.finish(_text(event, ".cave.remove", cave_id=cave_id))
        await matcher.send(_text(
            event, ".cave.remove.no-permission",
            cave_id=cave_id
        ))


@cave.command("checkout").handle()
async def cave_checkout_handle(
    matcher: Matcher,
    event: MessageEvent,
    arg: Message = CommandArg()
) -> None:
    branchs[str(event.user_id)] = branch = str(arg).strip()
    await matcher.send(text(event, ".checkout", branch=branch))


async def get_cave(
    cave_id: str,
    event: MessageEvent
) -> list[Message | list[ForwardNode]]:
    group_id = getattr(event, "group_id", None)
    messages = []
    branch_name, branch = get_branch(event)
    _text = partial(text, branch=branch_name)
    if not branch:
        return [_text(event, ".cave.empty")]
    if cave_id not in branch.keys():
        return [_text(event, ".cave.non-exist", cave_id=cave_id)]
    message = branch[cave_id]
    user_id = message["user_id"]
    content = message["content"]
    sender = escape(await get_user_name(user_id, group_id))
    if re.search(SPECIAL_PATTERN, content):
        messages.extend([Message(_text(
            event, ".cave.text.without-content",
            cave_id=cave_id,
            sender=sender
        )), Message(content)])
    else:
        messages.append(Message(_text(
            event, ".cave.text",
            cave_id=cave_id,
            content=content,
            sender=sender
        )))
    if comments := branch[cave_id].get("comments"):
        messages.append([
            await custom_forward_node(
                comment["content"],
                user_id := comment["user_id"],
                group_id=group_id,
                name=_text(
                    event, ".comment.text",
                    sender=await get_user_name(user_id),
                    comment_id=comment_id
                ),
                time=comment["time"]
            ) for comment_id, comment in cast(dict, comments).items()
        ])
    return messages


async def send_cave(cave_id: str, event: MessageEvent) -> None:
    for message in await get_cave(cave_id, event):
        await send(event, message)


def get_branch(event: MessageEvent) -> tuple[str, JsonDict[str, dict]]:
    branch_name = branch = branchs[str(event.user_id)]
    if branch == "session":
        branch = Path(event.message_type, str(get_session_id(event)))
    return branch_name, JsonDict(Path("caves", f"{branch}.json"), dict)
