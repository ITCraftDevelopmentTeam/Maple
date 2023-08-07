import re
from functools import partial
from pathlib import Path
from typing import Optional, Any, Literal   # this `Literal` is for `eval`

import yaml

from nonebot.adapters.onebot.v11 import MessageEvent

from ._onebot import UserID
from ._store import JsonDict


lang_use = JsonDict("lang.use.json", lambda: "zh-hans")
langs = {}
for path in Path("langs").glob("[!_]*"):
    with open(path, "r", encoding="utf-8") as file:
        langs[path.stem] = yaml.safe_load(file)
LangTag = eval("Literal['" + "','".join(langs.keys()) + "']")
LangType = LangTag | UserID | MessageEvent


def get_lang(lang: LangType) -> LangTag:
    if hasattr(lang, "user_id"):
        lang = lang.user_id
    lang = str(lang)
    if lang.isdecimal():
        lang = lang_use[lang]
    return lang


def parse(__string: str, __lang: LangType, /, **kwargs: Any) -> str:
    string, lang = __string.strip(), get_lang(__lang)
    # `text()`
    string = re.sub(
        pattern=r"{{%.*?%}}", string=string,
        repl=lambda macth: "{{ text(f'" + macth.group()[3:-3].strip() + "') }}"
    )
    # list comprehension
    string = re.sub(
        pattern=r"{{\$.*?\$}}", string=string, flags=re.DOTALL,
        repl=lambda macth: "{{ '\\n'.join([" + macth.group()[3:-3] + "]) }}"
    )
    # embedded Python code
    string = re.sub(
        pattern=r"{{.*?}}", string=string, flags=re.DOTALL,
        repl=lambda macth: str(eval(macth.group()[2:-2].strip(), {
            "__lang__": lang,
            "text": partial(text, lang, **kwargs),
            **kwargs
        }))
    )
    return string.replace("\{", "{").replace("\}", "}")


def text(
    __lang: LangType,
    __key: str,
    /,
    prefix: Optional[str] = "",
    escape_blank_key: bool = True,
    **kwargs: Any
) -> Optional[Any]:
    lang, key = get_lang(__lang), prefix + __key

    def gets(data: dict, key: str) -> Optional[Any]:
        for subkey in key.split("."):
            data = data[subkey]
        return data

    try:
        data = gets(langs[lang], key)
    except KeyError:
        lang = lang_use.default_factory()
        data = gets(langs[lang], key)

    if escape_blank_key and isinstance(data, dict) and "" in data.keys():
        data = data[""]
    if isinstance(data, str):
        return parse(data, lang, **kwargs)
    return data
