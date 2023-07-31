from typing import cast

from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, MessageEvent

from ._lang import parse, text


@on_command("help").handle()
async def help_handle(
    matcher: Matcher,
    event: MessageEvent,
    arg: Message = CommandArg()
) -> None:
    helps = cast(dict, text(event, "help", escape_blank_key=False))
    if (key := str(arg)) in helps.keys():
        await matcher.send(parse(helps[key], event))
