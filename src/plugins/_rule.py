from typing import Optional

from nonebot.rule import Rule
from nonebot.adapters.onebot.v11.event import Event

from ._gocq import UserId, GroupId


def user(user_id: UserId) -> Rule:
    def wapper(event: Event):
        return int(user_id) == getattr(event, 'user_id', -1)
    return Rule(wapper)


def group(group_id: GroupId) -> Rule:
    def wapper(event: Event):
        return int(group_id) == getattr(event, 'group_id', -1)
    return Rule(wapper)


def session(
    event: Optional[Event] = None,
    *,
    user_id: Optional[UserId] = None,
    group_id: Optional[GroupId] = None
) -> Rule:
    if event is not None:
        user_id = getattr(event, 'user_id', user_id)
        group_id = getattr(event, 'group_id', group_id)

    def wapper(event: Event):
        return (user_id == getattr(event, 'user_id', None)
                and group_id == getattr(event, 'group_id', None))

    return Rule(wapper)
