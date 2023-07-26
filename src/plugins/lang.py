from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, MessageEvent

from . import _lang
from ._lang import text, lang_names as langs


@on_command("lang").handle()
async def lang_handle(
    matcher: Matcher,
    event: MessageEvent,
    arg: Message = CommandArg()
) -> None:
    user_id = str(event.user_id)
    match str(arg).strip():
        case  "-l":
            await matcher.send(text(user_id, "lang.list", langs=langs))
        case lang if lang in langs:
            _lang.lang_use[user_id] = lang
            await matcher.send(text(user_id, "lang.set", lang=lang))
        case _:
            await matcher.finish()
