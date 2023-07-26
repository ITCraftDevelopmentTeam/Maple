import os
from time import time
from datetime import date

from nonebot import require
from nonebot import on_command, on_message
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent

from nonebot_plugin_apscheduler import scheduler

from ._lang import text
from ._store import JsonDict
from ._onebot import get_group_name


require("nonebot_plugin_apscheduler")


def get_day_path() -> str:
    return os.path.join("hot", "days", f"{date.today().isoformat()}.json")


MINUTE = 60
HOUR = 3600

STAMPS_PATH = os.path.join("hot", "stamps.json")
DAY_PATH = get_day_path()
TOTAL_PATH = os.path.join("hot", "total.json")


@scheduler.scheduled_job("cron", day="*", id="update_day_path")
async def update_day_path() -> None:
    global DAY_PATH
    DAY_PATH = get_day_path()


@scheduler.scheduled_job("cron", minute="*/10", id="update_stamps")
async def update_stamps() -> None:
    stamps = JsonDict(STAMPS_PATH, list[int])
    for group_id, group_stamps in stamps.items():
        stamps[group_id] = filter_stamps(group_stamps)


def filter_stamps(stamps: list[int], expire_time: int = HOUR) -> list[int]:
    return list(filter(lambda x: int(time()) - x <= expire_time, stamps))


@on_message().handle()
async def hot_counter_handle(event: GroupMessageEvent) -> None:
    stamps = JsonDict(STAMPS_PATH, list[int])
    stamps[str(event.group_id)].append(event.time)
    JsonDict(DAY_PATH)[str(event.group_id)] += 1
    JsonDict(TOTAL_PATH)[str(event.group_id)] += 1


@on_command("hot").handle()
async def hot_handle(
    matcher: Matcher,
    event: GroupMessageEvent,
    arg: Message = CommandArg()
) -> None:
    match str(arg).strip():
        case "":
            key = "hot.10min"
            stamps = JsonDict(STAMPS_PATH, list[int])
            ranks = [(group_id, len(filter_stamps(group_stamps, 10*MINUTE)))
                     for group_id, group_stamps in stamps.items()]
        case "-h":
            key = "hot.hour"
            stamps = JsonDict(STAMPS_PATH, list[int])
            ranks = [(group_id, len(filter_stamps(group_stamps, HOUR)))
                     for group_id, group_stamps in stamps.items()]
        case "-d":
            key = "hot.day"
            ranks = JsonDict(DAY_PATH).items()
        case "-t":
            key = "hot.total"
            ranks = JsonDict(TOTAL_PATH).items()
        case _:
            await matcher.finish()
    ranks = [(await get_group_name(group_id), count, int(group_id))
             for group_id, count in ranks if count != 0]
    ranks.sort(key=lambda x: x[1], reverse=True)
    await matcher.send(text(event.user_id, key, ranks=ranks, event=event))
