import os
import re
from functools import partial
from typing import Optional, Any, Literal   # this `Literal` is for `eval`

import yaml

from nonebot.adapters.onebot.v11 import MessageEvent

from ._onebot import UserID
from ._store import JsonDict


lang_use = JsonDict("lang_use.json", lambda: "zh-hans")
langs = {}
for filename in os.listdir("lang"):
    lang = os.path.splitext(filename)[0]
    file_path = os.path.join("lang", filename)
    with open(file_path, "r", encoding="utf-8") as file:
        langs[lang] = yaml.safe_load(file)
LangTag = eval("Literal['" + "','".join(langs.keys()) + "']")
LangType = LangTag | UserID | MessageEvent


def get_lang(lang: LangType) -> LangTag:
    if hasattr(lang, "user_id"):
        lang = lang.user_id
    lang = str(lang)
    if lang.isdecimal():
        lang = lang_use[lang]
    return lang


def parse(__text: str, /, **kwargs: Any) -> str:
    def repl(match: re.Match[str]) -> str:
        expr = match.group()[2:-2]
        return str(eval(expr.strip(), kwargs))

    return re.sub("{{.*?}}", repl, __text, flags=re.DOTALL)


def text(__lang: LangType, __key: str, /, **kwargs: Any) -> Optional[Any]:
    lang, key = get_lang(__lang), __key

    def gets(data: dict, __key: str) -> Optional[Any]:
        try:
            for subkey in __key.split("."):
                data = data[subkey]
        except KeyError:
            data = None
        return data

    try:
        data = gets(langs[lang], key)
    except KeyError:
        lang = lang_use.default_factory()
        data = gets(langs[lang], key)

    if isinstance(data, str):
        return parse(data, **{
            "__lang__": lang,
            "text": partial(text, lang, **kwargs),
            **kwargs
        })
    return data
