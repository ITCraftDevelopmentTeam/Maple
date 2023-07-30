from typing import Optional

from nonebot.rule import Rule
from nonebot.adapters.onebot.v11.event import Event

from ._onebot import UserID, GroupID


def user(user_id: UserID) -> Rule:
    def wapper(event: Event):
        return int(user_id) == getattr(event, "user_id", -1)
    return Rule(wapper)


def group(group_id: GroupID) -> Rule:
    def wapper(event: Event):
        return int(group_id) == getattr(event, "group_id", -1)
    return Rule(wapper)


def session(
    event: Optional[Event] = None,
    *,
    user_id: Optional[UserID] = None,
    group_id: Optional[GroupID] = None
) -> Rule:
    if event is not None:
        user_id = getattr(event, "user_id", None)
        group_id = getattr(event, "group_id", None)
    match user_id, group_id:
        case None, None:
            def wapper():
                return True
        case _, None:
            def wapper(event: Event):
                return user_id == getattr(event, "user_id", -1)
        case None, _:
            def wapper(event: Event):
                return group_id == getattr(event, "group_id", -1)
        case _, _:
            def wapper(event: Event):
                return (user_id == getattr(event, "user_id", -1) and
                        group_id == getattr(event, "group_id", -1))
    return Rule(wapper)
