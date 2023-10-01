import re
import traceback
from collections import defaultdict
from pathlib import Path
from typing import cast, Union, Optional, Any, Tuple, Dict, Callable, Literal

import yaml

from nonebot.adapters.onebot.v11 import MessageEvent

from ._gocq import UserId
from ._store import Json
from ._sorcery import modulename, getframe


# TODO: LangTag = eval('Literal['' + '',''.join(langs.keys()) + '']')
LangTag = Literal['zh-hans']
LangType = LangTag | UserId | MessageEvent
Tree = Dict[str, Union[Any, 'Tree']]
langs: Dict[LangTag, Tree] = {}
for path in Path('langs').glob('[!_]*'):
    with open(path, 'r', encoding='utf-8') as file:
        langs[cast(LangTag, path.stem)] = yaml.safe_load(file)
lang_users = Json('.users', defaultdict[UserId, LangTag], lambda: 'zh-hans')


def get_lang(lang: LangType) -> LangTag:
    if lang in langs.keys():
        return cast(LangTag, lang)
    lang = cast(LangTag, getattr(lang, 'user_id', cast(LangTag, lang)))
    return lang_users._[lang]


def parse(__string: str, __lang: LangType, /, **kwargs: Any) -> str:
    string, lang = __string.strip(), get_lang(__lang)
    # comment
    string = re.sub(r'{{#(.*?)#}}', string=string, flags=re.DOTALL, repl='')
    # `text()`
    string = re.sub(r'{{%(.*?)%}}', string=string, flags=re.DOTALL,
                    repl=lambda m: "{{text(f'" + m.group(1).strip() + "')}}")
    # list comprehension
    string = re.sub(r'{{\$(.*?)\$}}', string=string, flags=re.DOTALL,
                    repl=lambda m: "{{'\\n'.join([' + m.group(1) + '])}}")

    def repl(match: re.Match[str]) -> str:
        try:
            return str(eval(match[1].strip(), {
                '__lang__': lang,
                'text': text,
                **kwargs
            }))
        except Exception:
            return traceback.format_exc()

    # embedded Python code
    string = re.sub(r'{{(.*?)}}', repl=repl, string=string, flags=re.DOTALL)
    return string.replace(r'\{', '{').replace(r'\}', '}')


def _get(
    key: str,
    lang: Optional[LangType] = None,
    depth: int = 0
) -> Tuple[Tree | str, str, LangTag]:
    if lang is None:
        lang = getframe(depth + 1).f_locals['event']
    lang = get_lang(cast(LangType, lang))
    if key.startswith('.'):
        key = modulename(depth + 1) + key

    def gets(data: Tree, key: str) -> Tree | str:
        for subkey in key.split('.'):
            data = cast(Tree, data[subkey])
        return data

    try:
        data = gets(langs[lang], key)
    except KeyError:
        lang = cast(Callable[[], LangTag], lang_users.factory())()
        data = gets(langs[lang], key)
    return data, key, lang


def raw(
    __key: str,
    __lang: Optional[LangType] = None,
    /,
    **kwargs: Any
) -> Tree | str:
    return _get(__key, __lang, **kwargs, depth=1)[0]


def text(
    __key: str,
    __lang: Optional[LangType] = None,
    /,
    **kwargs: Any
) -> str:
    data, _, lang = _get(__key, __lang, **kwargs, depth=1)

    if isinstance(data, dict) and '' in data.keys():
        data = data['']
    assert isinstance(data, str)
    return parse(data, lang, **kwargs)
