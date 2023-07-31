import os
from functools import partial
from time import time

from nonebot import require, on_message, CommandGroup
from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent

require("nonebot_plugin_apscheduler")

from nonebot_plugin_apscheduler import scheduler

from ._lang import text
from ._store import JsonDict
from ._onebot import send, get_group_name, GroupID


text = partial(text, prefix="hot")

stamps = JsonDict(os.path.join("hot", "stamps.json"), list[int])
day = JsonDict(os.path.join("hot", "day.json"), int)
total = JsonDict(os.path.join("hot", "total.json"), int)
hot = CommandGroup("hot")

MINUTE = 60
HOUR = 3600


@on_message().handle()
async def hot_counter_handle(event: GroupMessageEvent) -> None:
    stamps[str(event.group_id)].append(event.time)
    day[str(event.group_id)] += 1
    total[str(event.group_id)] += 1


@hot.command(tuple()).handle()
async def hot_10min_handle(event: MessageEvent) -> None:
    await send_hot(event, ".10min", [
        (group_id, len(filter_stamps(group_stamps, 10*MINUTE)))
        for group_id, group_stamps in stamps.items()
    ])


@hot.command("hour").handle()
async def hot_hour_handle(event: MessageEvent) -> None:
    await send_hot(event, ".hour", [
        (group_id, len(filter_stamps(group_stamps, HOUR)))
        for group_id, group_stamps in stamps.items()
    ])


@hot.command("day").handle()
async def hot_day_handle(event: MessageEvent) -> None:
    await send_hot(event, ".day", day.items())


@hot.command("total").handle()
async def hot_total_handle(event: MessageEvent) -> None:
    await send_hot(event, ".total", total.items())


@scheduler.scheduled_job("cron", minute="*/10", id="update_stamps")
async def update_stamps() -> None:
    for group_id, group_stamps in stamps.items():
        stamps[group_id] = filter_stamps(group_stamps)


@scheduler.scheduled_job("cron", day="*", id="update_day")
async def update_day() -> None:
    for key in day.keys():
        day.pop(key)


async def send_hot(
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
