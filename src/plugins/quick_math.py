import asyncio
from datetime import timedelta
from functools import partial
from random import randint, choice, random
from typing import cast

from sympy import simplify, Rational, factorint

from nonebot import on_command, on_regex
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, MessageEvent

from ._credit import credits
from ._lang import text
from ._onebot import (
    send, delete_msg,
    get_session_id,
    UserID, GroupID
)
from ._rule import session
from ._store import JsonDict

text = partial(text, prefix="quick-math")

disableds = JsonDict("quick-math.disableds.json", list[UserID] | list[GroupID])

EXPIRE_TIME = timedelta(seconds=10)


@on_command("quick-math", aliases={"qm"}).handle()
async def quick_math_handler(
    event: MessageEvent,
    arg: Message = CommandArg()
) -> None:
    match str(arg).strip():
        case  "":
            if random() < 0.05 and (eggs := text(event, ".eggs")):
                question, answer = choice(list(cast(dict, eggs).items()))
            else:
                a = randint(1, 10)
                b = randint(1, 10)
                op = choice(["+", "-", "*", "/", "%", "//", "**"])
                if op == "**":
                    b = randint(0, 3)
                question = text(event, ".question", a=a, op=op, b=b)
                answer = cast(Rational, simplify(f"{a}{op}{b}"))
                if (frac := answer).q != 1:
                    answer = rf"{answer.p}\s*?[/÷]\s*?{answer.q}"
                    if not set(factorint(frac.q, limit=10).keys()) - {2, 5}:
                        answer += f"|{frac.p/frac.q}"

            message_id = await send(event, question)

            @on_regex(
                rf"^\s*?{answer}\s*?$",
                rule=session(event),
                temp=True,
                expire_time=EXPIRE_TIME
            ).handle()
            async def quick_math_answer_handler(
                matcher: Matcher,
                succ_event: MessageEvent
            ) -> None:
                credit = randint(1, 3)
                credits[str(succ_event.user_id)] += credit
                await matcher.send(text(
                    str(succ_event.user_id), ".correct",
                    got=credit, total=credits[str(succ_event.user_id)]
                ), at_sender=True)
                if (get_session_id(succ_event)
                        not in disableds[succ_event.message_type]):
                    await quick_math_handler(succ_event, "")

            await asyncio.sleep(EXPIRE_TIME.total_seconds())
            await delete_msg(message_id)

        case "on":
            event_id = get_session_id(event)
            if event_id in disableds[event.message_type]:
                disableds[event.message_type].remove(event_id)
            await send(event, text(event, ".auto.on"))

        case "off":
            event_id = get_session_id(event)
            if event_id not in disableds[event.message_type]:
                disableds[event.message_type].append(event_id)
            await send(event, text(event, ".auto.off"))
