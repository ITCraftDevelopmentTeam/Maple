from ._onebot import send, get_group_name, GroupID
from ._store import JsonDict
from ._lang import text
from nonebot_plugin_apscheduler import scheduler
import os
from time import time
from datetime import date

from nonebot import require
from nonebot import CommandGroup, on_message
from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent


require("nonebot_plugin_apscheduler")


def get_day_path() -> str:
    return os.path.join("hot", "days", f"{date.today().isoformat()}.json")


MINUTE = 60
HOUR = 3600

stamps = JsonDict(os.path.join("hot", "stamps.json"), list[int])
day = JsonDict(get_day_path(), int)
total = JsonDict(os.path.join("hot", "total.json"), int)
hot = CommandGroup("hot")


@on_message().handle()
async def hot_counter_handle(event: GroupMessageEvent) -> None:
    stamps[str(event.group_id)].append(event.time)
    day[str(event.group_id)] += 1
    total[str(event.group_id)] += 1


@hot.command(tuple()).handle()
async def hot_handle(event: MessageEvent) -> None:
    await show_rank("hot.10min", [
        (group_id, len(filter_stamps(group_stamps, 10*MINUTE)))
        for group_id, group_stamps in stamps.items()
    ])


@hot.command("hour").handle()
async def hot_hour_handle(event: MessageEvent) -> None:
    await show_rank("hot.hour", [
        (group_id, len(filter_stamps(group_stamps, HOUR)))
        for group_id, group_stamps in stamps.items()
    ])


@hot.command("day").handle()
async def hot_day_handle(event: MessageEvent) -> None:
    await show_rank("hot.day", day.items())


@hot.command("total").handle()
async def hot_total_handle(event: MessageEvent) -> None:
    await show_rank("hot.total", total.items())


@scheduler.scheduled_job("cron", minute="*/10", id="update_stamps")
async def update_stamps() -> None:
    for group_id, group_stamps in stamps.items():
        stamps[group_id] = filter_stamps(group_stamps)


@scheduler.scheduled_job("cron", day="*", id="update_day_path")
async def update_day_path() -> None:
    global day
    day = JsonDict(get_day_path(), int)


async def show_rank(
    event: MessageEvent,
    key: str,
    ranks: list[tuple[GroupID, int]]
) -> None:
    ranks = [
        (await get_group_name(group_id), count, int(group_id))
        for group_id, count in ranks
        if count != 0
    ]
    ranks.sort(key=lambda x: x[1], reverse=True)
    await send(event, text(event, key, ranks=ranks, event=event))


def filter_stamps(stamps: list[int], expire_time: int = HOUR) -> list[int]:
    return list(filter(lambda x: int(time()) - x <= expire_time, stamps))
