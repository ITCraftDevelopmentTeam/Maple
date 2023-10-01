from typing import cast

from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, MessageEvent

from ._lang import parse, raw


@on_command('help').handle()
async def help_handler(
    matcher: Matcher,
    event: MessageEvent,
    arg: Message = CommandArg()
) -> None:
    helps = cast(dict, raw('help'))
    if (key := str(arg)) in helps.keys():
        await matcher.send(parse(helps[key], event))
