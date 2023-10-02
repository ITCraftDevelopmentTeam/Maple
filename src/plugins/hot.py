from time import time

from nonebot import require, on_message, CommandGroup
from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent

require("nonebot_plugin_apscheduler")

from nonebot_plugin_apscheduler import scheduler

from ._gocq import send_by, groupname, GroupId
from ._store import Json
from ._lang import text


stamps = Json('.stamps', dict[GroupId, list[int]])
day = Json('.day', dict[GroupId, int])
total = Json('.total', dict[GroupId, int])
hot = CommandGroup('hot')

MINUTE = 60
HOUR = 3600


@on_message().handle()
async def hot_counter_handler(event: GroupMessageEvent) -> None:
    with stamps as _stamps, day as _day, total as _total:
        _stamps[str(event.group_id)].append(event.time)
        _day[str(event.group_id)] += 1
        _total[str(event.group_id)] += 1


@hot.command(tuple()).handle()
async def hot_10min_handler(event: MessageEvent) -> None:
    await send_hot(event, '.10min', [
        (group_id, len(filter_stamps(group_stamps, 10*MINUTE)))
        for group_id, group_stamps in stamps._.items()
    ])


@hot.command('hour').handle()
async def hot_hour_handler(event: MessageEvent) -> None:
    await send_hot(event, '.hour', [
        (group_id, len(filter_stamps(group_stamps, HOUR)))
        for group_id, group_stamps in stamps._.items()
    ])


@hot.command('day').handle()
async def hot_day_handler(event: MessageEvent) -> None:
    await send_hot(event, '.day', list(day._.items()))


@hot.command('total').handle()
async def hot_total_handler(event: MessageEvent) -> None:
    await send_hot(event, '.total', list(total._.items()))


@scheduler.scheduled_job('cron', minute='*/10', id='update_stamps')
async def update_stamps() -> None:
    with stamps as _stamps:
        for group_id, group_stamps in _stamps.items():
            _stamps[group_id] = filter_stamps(group_stamps)


@scheduler.scheduled_job('cron', day='*', id='update_day')
async def update_day() -> None:
    with day as _day:
        _day.clear()


async def send_hot(
    event: MessageEvent,
    key: str,
    group_id_and_counts: list[tuple[GroupId, int]]
) -> None:
    if (id_name_counts := [
        (int(group_id), await groupname(group_id), count)
        for group_id, count in group_id_and_counts if count
    ]):
        id_name_counts.sort(key=lambda x: x[-1], reverse=True)
        await send_by(event, text(key, ranks=id_name_counts, event=event))
    else:
        await send_by(event, text('.none'))


def filter_stamps(stamps: list[int], expire_time: int = HOUR) -> list[int]:
    return list(filter(lambda x: int(time()) - x <= expire_time, stamps))
