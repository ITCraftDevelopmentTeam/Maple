from nonebot import on_command
from nonebot.permission import SUPERUSER
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, unescape


@on_command("echo", permission=SUPERUSER).handle()
async def lang_handle(matcher: Matcher, arg: Message = CommandArg()) -> None:
    await matcher.send(Message(unescape(str(arg))))
