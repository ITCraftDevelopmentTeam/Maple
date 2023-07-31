from functools import partial

from nonebot import CommandGroup
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, MessageEvent

from ._lang import text, langs, lang_use


text = partial(text, prefix="lang")
lang = CommandGroup("lang")


@lang.command(tuple()).handle()
async def lang_set_handle(
    matcher: Matcher,
    event: MessageEvent,
    arg: Message = CommandArg()
) -> None:
    if (lang := str(arg)) in langs:
        lang_use[str(event.user_id)] = lang
        await matcher.finish(text(event, ".set", lang=lang))
    await matcher.send(text(event, ".non-exist", lang=lang))


@lang.command("list").handle()
async def lang_list_handle(matcher: Matcher, event: MessageEvent) -> None:
    await matcher.send(text(event, ".list", langs=langs))


@lang.command("add").handle()
async def lang_add_handle(matcher: Matcher, event: MessageEvent) -> None:
    await matcher.send(text(event, ".add"))
