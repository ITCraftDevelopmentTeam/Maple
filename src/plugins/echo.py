import re

from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import Message, MessageEvent, unescape

from ._lang import parse
from .github import unescape_emoji


@on_command("echo", permission=SUPERUSER).handle()
async def echo_handler(
    matcher: Matcher,
    event: MessageEvent,
    arg: Message = CommandArg()
) -> None:
    arg = unescape(str(arg))
    arg = parse(arg, event)
    arg = unescape_unicode(arg)
    arg = unescape_emoji(arg)
    await matcher.send(Message(arg))


def unescape_unicode(string: str) -> str:
    return re.sub(
        r"u\+[0-9a-f]+", string=string.lower(),
        repl=lambda match: chr(int(match.group()[2:], base=16))
    )
