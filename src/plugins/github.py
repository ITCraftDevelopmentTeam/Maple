from functools import partial

import requests

from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, MessageEvent

from ._lang import text


text = partial(text, prefix="github")


@on_command("github", aliases={"gh"}).handle()
async def github_handle(
    matcher: Matcher,
    event: MessageEvent,
    arg: Message = CommandArg()
) -> None:
    arg: str = str(arg).replace("https://github.com", "").strip(" /")
    if len(args := arg.split("/")) >= 3 and args[2] == "pull":
        args[2] = "pulls"       # fuck you, GayHub!
        arg = "/".join(args)
    url = f"https://api.github.com/repos/{arg}"
    data: dict = requests.get(url, verify=False).json()
    if data.get("message") == "Not Found":
        await matcher.finish(text(event, ".non-exist", arg=arg))
    match tuple(args):
        case owner, repo:
            await matcher.send(text(event, ".repo", data=data))
        case owner, repo, "issues", number:
            await matcher.send(text(event, ".issue", data=data))
        case owner, repo, "pulls", number:
            await matcher.send(text(event, ".pull", data=data))
        case _:
            await matcher.send(text(event, ".nonsupport", arg=arg))
