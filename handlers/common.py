from aiogram import Router, types
from aiogram.filters import Command

from database.dbConnectionCM import DatabaseConnection

router = Router()


@router.message(Command("group"))
async def group_change_command(message: types.Message):

    with DatabaseConnection() as connection_db:
        info = connection_db.execute(f'SELECT * FROM users WHERE userid = {message.from_user.id}').fetchone()
        if info is None:
            await message.answer(f"Пользователь {message.from_user.id} отсутствует в базе ✘")
            return

        if info[1] == 1:
            connection_db.execute(f"UPDATE users SET groupnum = 2 WHERE userid = {message.from_user.id}")
            await message.answer(f"Группа пользователя {message.from_user.username} изменена на 2")
        if info[1] == 2:
            connection_db.execute(f"UPDATE users SET groupnum = 1 WHERE userid = {message.from_user.id}")
            await message.answer(f"Группа пользователя {message.from_user.username} изменена на 1")
        connection_db.commit()


@router.message(Command("broadcast"))
async def group_change_command(message: types.Message):

    with DatabaseConnection() as connection_db:
        info = connection_db.execute(f'SELECT * FROM users WHERE userid = {message.from_user.id}').fetchone()
        if info is None:
            await message.answer(f"Пользователь {message.from_user.id} отсутствует в базе ✘")
            return

        if info[3] == 0:
            connection_db.execute(f"UPDATE users SET broadcast = 1 WHERE userid = {message.from_user.id}")
            await message.answer(f"Рассылка расписания включена ✅ (19:00)")
        if info[3] == 1:
            connection_db.execute(f"UPDATE users SET broadcast = 0 WHERE userid = {message.from_user.id}")
            await message.answer(f"Рассылка расписания отключена ❌")
        connection_db.commit()
