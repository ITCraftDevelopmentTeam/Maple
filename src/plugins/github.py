import re
from functools import partial

import requests

from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, MessageSegment, MessageEvent

from ._lang import text
from ._store import JsonDict


text = partial(text, prefix="github")

if not (emojis := JsonDict("github.emojis.json", str)):
    url = "https://api.github.com/emojis"
    emojis.update(requests.get(url, verify=False).json())


@on_command("github", aliases={"gh"}).handle()
async def github_handler(
    matcher: Matcher,
    event: MessageEvent,
    arg: Message = CommandArg()
) -> None:
    arg: str = (
        arg
        .extract_plain_text()
        .replace("https://", "")
        .replace("github.com", "")
        .strip(" /")
    )
    if len(args := arg.split("/")) >= 3 and not args[2].endswith("s"):
        args[2] += "s"
    url = f"https://api.github.com/repos/{'/'.join(args)}"
    data: dict = requests.get(url, verify=False).json()
    if data.get("message") == "Not Found":
        await matcher.finish(text(event, ".non-exist", arg=arg))
    match tuple(args):
        case owner, repo:
            string = text(event, ".repo", data=data)
        case owner, repo, "issues", number:
            string = text(event, ".issue", data=data)
        case owner, repo, "pulls", number:
            string = text(event, ".pull", data=data)
        case owner, repo, "commits", number:
            string = text(event, ".commit", data=data)
        case _:
            await matcher.finish(text(event, ".nonsupport", arg=arg))
    await matcher.send(unescape_emoji(string))


def unescape_emoji(string: str, *, as_image: bool = False) -> str:
    def repl(match: re.Match[str]) -> str:
        emoji_id = match.group()[1:-1]
        if emoji_id not in emojis.keys():
            return match.group()
        if as_image:
            return str(MessageSegment.image(emojis[emoji_id]))
        return "\u200d".join(map(
            lambda x: chr(int(x, base=16)),
            emojis[emoji_id][59:-7].split("-")
        ))

    return re.sub(r":[a-zA-Z0-9_]+?:", string=string, repl=repl)
