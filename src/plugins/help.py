from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import MessageEvent

from ._lang import text
from .lang import lang
from .hot import hot
from .cave import cave


@lang.command("help").handle()
async def lang_help_handle(matcher: Matcher, event: MessageEvent) -> None:
    await matcher.send(text(event, "lang.help"))


@hot.command("help").handle()
async def hot_help_handle(matcher: Matcher, event: MessageEvent) -> None:
    await matcher.finish(text(event, "hot.help"))


@cave.command("help").handle()
async def cave_help_handle(matcher: Matcher, event: MessageEvent) -> None:
    await matcher.send(text(event, "cave.help"))
