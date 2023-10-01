from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import Message, MessageEvent

from ._lang import parse
from ._utils import unescape_emoji


@on_command('echo', permission=SUPERUSER).handle()
async def echo_handler(
    matcher: Matcher,
    event: MessageEvent,
    arg: Message = CommandArg()
) -> None:
    await matcher.send(Message(unescape_emoji(parse(str(arg), event))))
