from typing import Optional

from nonebot.rule import Rule
from nonebot.adapters.onebot.v11.event import Event

from ._gocq import UserId, GroupId


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


def user(user_id: UserId) -> Rule:
    return session(user_id=user_id)


def group(group_id: GroupId) -> Rule:
    return session(group_id=group_id)
