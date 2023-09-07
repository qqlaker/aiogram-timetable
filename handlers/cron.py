import datetime

from aiogram import Bot

from database.dbConnectionCM import DatabaseConnection

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


async def change_week_cron():
    with open('config/week.txt', 'r') as file:
        filedata = file.read()
    if filedata == "chisl":
        filedata = "znamen"
    elif filedata == "znamen":
        filedata = "chisl"
    with open('config/week.txt', 'w') as file:
        file.write(filedata)


async def send_message_cron(bot: Bot):
    with open("config/week.txt", 'r') as wf:
        week = wf.readline().strip('\n')

    with DatabaseConnection() as connection_db:
        connection_db.row_factory = lambda cursor, row: row[0]
        c = connection_db.cursor()
        user_ids = c.execute("SELECT userid FROM users").fetchall()
        for userid in user_ids:
            connection_db.row_factory = lambda cursor, row: row
            row = connection_db.execute(f"SELECT * FROM users WHERE userid = {userid}").fetchone()
            if row is not None:
                if not (bool(row[2]) is False and bool(row[3]) is True):
                    continue
                group_num = row[1]

                connection_db.row_factory = dict_factory
                cur = connection_db.cursor()
                # TODO: можно оптимизировать (хранить таблицы в кеше, а не обращаться с каждым пользователем)
                cur.execute(f"SELECT * FROM shedule_{group_num}group_{week}")
                result = cur.fetchall()

                current_week_day = datetime.datetime.today().weekday()
                if current_week_day == 6:
                    current_week_day = -1
                if current_week_day == 5:
                    last_msg = await bot.send_message(userid, f"☑ Расписание на завтра | {week}, группа - {group_num}\n---- занятий нет ----")
                    await bot.pin_chat_message(userid, last_msg.message_id)
                    continue
                await bot.send_message(userid, f"☑ Расписание на завтра | {week}, группа - {group_num}")
                key = week_days[current_week_day + 1]
                msg = msg_builder(key, result)
                last_msg = await bot.send_message(userid, text=msg)
                await bot.pin_chat_message(userid, last_msg.message_id)
                return
