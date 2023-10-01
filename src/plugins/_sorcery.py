from inspect import currentframe
from types import FrameType
from typing import cast


def getframe(depth: int = 0) -> FrameType:
    frame = cast(FrameType, currentframe())
    for _ in range(depth + 1):
        frame = cast(FrameType, frame.f_back)
    return frame


def modulename(depth: int = 0) -> str:
    modulename = cast(str, getframe(depth + 1).f_globals['__name__'])
    return modulename.lstrip('src.').lstrip('plugins.')


def funcname(depth: int = 0) -> str:
    return getframe(depth + 1).f_code.co_name
