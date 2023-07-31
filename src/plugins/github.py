import re
from functools import partial

import requests

from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, MessageEvent

from ._lang import text


text = partial(text, prefix="github")


@on_command("github", aliases={"gh"}).handle()
async def github_repo_handle(
    matcher: Matcher,
    event: MessageEvent,
    arg: Message = CommandArg()
) -> None:
    if found := re.findall("(.*)/(.*)", str(arg)):
        owner, repo = found[0]
        url = f"https://api.github.com/repos/{owner}/{repo}"
        data = requests.get(url, verify=False).json()
        await matcher.finish(text(event, ".repo", data=data))
    await matcher.send(text(event, ".repo.non-exist", owner=owner, repo=repo))
