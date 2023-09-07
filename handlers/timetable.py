import datetime

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from database.dbConnectionCM import DatabaseConnection

router = Router()

week_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def msg_builder(key, result):
    stra = f"{key}:\n"
    for row in result:
        stra += f"{row['Time']} - "
        if row[key] is not None:
            stra += f"{row[key]}"
        stra += "\n"
    return stra


@router.message(Command("week", "today", "tomorrow"))
async def cmd_timetable(message: Message, command: CommandObject):

    with open("config/week.txt", 'r') as wf:
        week = wf.readline().strip('\n')

    with DatabaseConnection() as connection_db:
        info = connection_db.execute(f'SELECT * FROM users WHERE userid = {message.from_user.id}').fetchone()
        if info is None:
            await message.answer(f"Пользователь {message.from_user.id} отсутствует в базе ✘")
            return

        group_num = info[1]
        connection_db.row_factory = dict_factory
        cur = connection_db.cursor()
        cur.execute(f"SELECT * FROM shedule_{group_num}group_{week}")
        result = cur.fetchall()

        if command.command == "week":
            await message.answer(f"☑ Расписание на неделю | {week}, группа - {group_num}")
            for key in week_days:
                msg = msg_builder(key, result)
                await message.answer(text=msg)
            return

        current_week_day = datetime.datetime.today().weekday()
        if command.command == "today":
            if current_week_day == 6:
                await message.answer(f"☑ Расписание на сегодня | {week}, группа - {group_num}\n---- занятий нет ----")
                return
            await message.answer(f"☑ Расписание на сегодня | {week}, группа - {group_num}")
            key = week_days[current_week_day]
            msg = msg_builder(key, result)
            await message.answer(text=msg)
            return

        if command.command == "tomorrow":
            if current_week_day == 6:
                current_week_day = -1
                if week == "chisl":
                    week = "znamen"
                elif week == "znamen":
                    week = "chisl"
                connection_db.row_factory = dict_factory
                cur = connection_db.cursor()
                cur.execute(f"SELECT * FROM shedule_{group_num}group_{week}")
                result = cur.fetchall()
            if current_week_day == 5:
                await message.answer(f"☑ Расписание на завтра | {week}, группа - {group_num}\n---- занятий нет ----")
                return
            await message.answer(f"☑ Расписание на завтра | {week}, группа - {group_num}")
            key = week_days[current_week_day+1]
            msg = msg_builder(key, result)
            await message.answer(text=msg)
            return
