from nonebot import CommandGroup
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, MessageEvent

from ._lang import text, langs, lang_use


lang = CommandGroup("lang")


@lang.command(tuple()).handle()
async def lang_list_handle(
    matcher: Matcher,
    event: MessageEvent,
    arg: Message = CommandArg()
) -> None:
    if str(arg) in langs:
        lang_use[event.user_id] = lang
        await matcher.finish(text(event, "lang.set", lang=lang))
    await matcher.finish(text(event, "lang.non-exist", lang=lang))


@lang.command("list").handle()
async def lang_list_handle(matcher: Matcher, event: MessageEvent) -> None:
    await matcher.send(text(event, "lang.list", langs=langs))


@lang.command("add").handle()
async def lang_add_handle(matcher: Matcher, event: MessageEvent) -> None:
    await matcher.send(text(event, "lang.add"))
