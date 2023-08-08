import re
import traceback
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
    # comment
    string = re.sub(r"{{#(.*?)#}}", string=string, flags=re.DOTALL, repl="")
    # `text()`
    string = re.sub(r"{{%(.*?)%}}", string=string, flags=re.DOTALL,
                    repl=lambda m: "{{text(f'" + m.group(1).strip() + "')}}")
    # list comprehension
    string = re.sub(r"{{\$(.*?)\$}}", string=string, flags=re.DOTALL,
                    repl=lambda m: "{{'\\n'.join([" + m.group(1) + "])}}")

    def repl(match: re.Match[str]) -> str:
        try:
            return str(eval(match.group(1).strip(), {
                "__lang__": lang,
                "text": partial(text, lang, **kwargs),
                **kwargs
            }))
        except Exception:
            return traceback.format_exc()

    # embedded Python code
    string = re.sub(r"{{(.*?)}}", repl=repl, string=string, flags=re.DOTALL)
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
