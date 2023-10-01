from nonebot import CommandGroup
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, MessageEvent

from ._lang import text, langs, lang_users


lang = CommandGroup('lang')


@lang.command(tuple()).handle()
async def lang_set_handler(
    matcher: Matcher,
    event: MessageEvent,
    arg: Message = CommandArg()
) -> None:
    if (lang := str(arg)) in langs:
        lang_users._[str(event.user_id)] = lang
        await matcher.finish(text('.set', lang=lang))
    await matcher.send(text('.non-exist', lang=lang))


@lang.command('list').handle()
async def lang_list_handler(matcher: Matcher, event: MessageEvent) -> None:
    await matcher.send(text('.list', event, langs=langs))


@lang.command('add').handle()
async def lang_add_handler(matcher: Matcher, event: MessageEvent) -> None:
    await matcher.send(text('.add', event))
