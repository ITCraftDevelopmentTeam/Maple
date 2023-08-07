import re

from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import Message, unescape

from .github import unescape_emoji

@on_command("echo", permission=SUPERUSER).handle()
async def echo_handle(matcher: Matcher, arg: Message = CommandArg()) -> None:
    await matcher.send(unescape_emoji(unescape(str(arg))))
