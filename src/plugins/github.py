import httpx
from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, MessageEvent

from ._lang import text
from ._utils import unescape_emoji


@on_command('github', aliases={'gh'}).handle()
async def github_handler(
    matcher: Matcher,
    event: MessageEvent,
    arg: Message = CommandArg()
) -> None:
    path = (
        arg
        .extract_plain_text()
        .removeprefix('https://')
        .removeprefix('github.com')
        .strip(' /')
    )
    if len(paths := path.split('/')) >= 3 and not paths[2].endswith('s'):
        paths[2] += 's'
    url = f"https://api.github.com/repos/{'/'.join(paths)}"
    data: dict = httpx.get(url, verify=False).json()
    if data.get('message') == 'Not Found':
        await matcher.finish(text('.non-exist', path=path))
    match paths:
        case owner, repo:
            string = text('.repo', data=data)
        case owner, repo, 'issues', number:
            string = text('.issue', data=data)
        case owner, repo, 'pulls', number:
            string = text('.pull', data=data)
        case owner, repo, 'commits', number:
            string = text('.commit', data=data)
        case _:
            await matcher.finish(text('.nonsupport', path=path))
    await matcher.send(unescape_emoji(string))
