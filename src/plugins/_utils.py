import re

import httpx
from nonebot.adapters.onebot.v11 import MessageSegment

from ._store import Json

with Json('.emojis', dict[str, str]) as emojis:
    if not emojis:
        url = 'https://api.github.com/emojis'
        emojis.update(httpx.get(url, verify=False).json())


def unescape_emoji(string: str, *, as_image: bool = False) -> str:
    def repl(match: re.Match[str]) -> str:
        emoji_id = match.group(1)
        if emoji_id not in emojis.keys():
            return match.group()
        if as_image:
            return str(MessageSegment.image(emojis[emoji_id]))
        return '\u200d'.join(map(
            lambda x: chr(int(x, base=16)),
            emojis[emoji_id][59:-7].split('-')
            # .../images/icons/emoji/unicode/{unicode(s)}.png?v8
        ))

    return re.sub(r':([a-zA-Z0-9_]+?):', string=string, repl=repl)


def unescape_ascii(string: str) -> str:
    return re.sub(
        r'&#(\d+);', string=string, flags=re.IGNORECASE,
        repl=lambda match: chr(int(match.group(1)))
    )


def unescape_unicode(string: str) -> str:
    return re.sub(
        r'\\u([0-9a-f]+)', string=string, flags=re.IGNORECASE,
        repl=lambda match: chr(int(match.group(1), base=16))
    )
