import asyncio
from datetime import timedelta
from random import randint, choice, random
from typing import cast, TypedDict

from sympy import simplify, Rational, factorint

from nonebot import on_command, on_regex
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, MessageEvent

from ._lang import raw, text
from ._gocq import send_by, delete_msg, UserId, GroupId
from ._rule import session
from ._store import Json


class DisabledsType(TypedDict):
    private: list[UserId]
    group: list[GroupId]


disableds = Json('.disableds', DisabledsType, private=[], group=[])

EXPIRE_TIME = timedelta(seconds=10)


@on_command('quick-math', aliases={'qm'}).handle()
async def quick_math_handler(
    event: MessageEvent,
    arg: Message = CommandArg()
) -> None:
    match str(arg).strip():
        case '':
            if ((eggs := cast(dict[str, str], raw('.eggs')))
                    and random() < cast(float, raw('.probably'))):
                question, answer = choice(list(eggs.items()))
            else:
                a = randint(1, 10)
                b = randint(1, 10)
                op = choice(['+', '-', '*', '/', '%', '//', '**'])
                if op == '**':
                    b = randint(0, 3)
                question = text('.question', a=a, op=op, b=b)
                answer = cast(Rational, simplify(f'{a}{op}{b}'))
                if (frac := answer).q != 1:
                    answer = rf'{answer.p}\s*?[/÷]\s*?{answer.q}'
                    if not set(factorint(frac.q, limit=10).keys()) - {2, 5}:
                        answer += f'|{frac.p/frac.q}'

            message_id = await send_by(event, question)

            @on_regex(
                rf'^\s*?{answer}\s*?$',
                rule=session(event),
                temp=True,
                expire_time=EXPIRE_TIME
            ).handle()
            async def quick_math_answer_handler(
                matcher: Matcher,
                succ_event: MessageEvent
            ) -> None:
                credit = randint(1, 3)
                with Json('credits', dict[UserId, int]) as credits:
                    credits[str(succ_event.user_id)] += credit
                    await matcher.send(text(
                        '.correct', succ_event,
                        got=credit, total=credits[str(succ_event.user_id)]
                    ), at_sender=True)
                if (getattr(succ_event, 'group_id', event.user_id)
                        not in disableds._[succ_event.message_type]):
                    await quick_math_handler(succ_event, '')

            await asyncio.sleep(EXPIRE_TIME.total_seconds())
            await delete_msg(message_id)

        case 'on' | 'off' as switch:
            session_id = getattr(event, 'group_id', event.user_id)
            with disableds as _disableds:
                match switch:
                    case 'on':
                        if session_id in _disableds[event.message_type]:
                            _disableds[event.message_type].remove(session_id)
                    case 'off':
                        if session_id not in _disableds[event.message_type]:
                            _disableds[event.message_type].append(session_id)
            await send_by(event, text(f'.auto.{switch}'))
