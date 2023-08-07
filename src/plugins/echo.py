from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import Message, unescape as unescape_CQcode

from .github import unescape_emoji


@on_command("echo", permission=SUPERUSER).handle()
async def echo_handler(matcher: Matcher, arg: Message = CommandArg()) -> None:
    await matcher.send(Message(unescape_emoji(unescape_CQcode(str(arg)))))
