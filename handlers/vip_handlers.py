from aiogram import Router, Bot, F, types
from aiogram.filters.state import StatesGroup, State
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove

from database.dbConnectionCM import DatabaseConnection

router = Router()


def _is_super_user(user_id: int, connection_db) -> bool:
    row = connection_db.execute(f"SELECT * FROM users WHERE userid = {user_id}").fetchone()
    if row is not None:
        return bool(row[4])
    return False


@router.message(Command("message_all"))
async def message_all_command(message: types.Message, command: CommandObject, bot: Bot):
    with DatabaseConnection() as connection_db:
        if not _is_super_user(message.from_user.id, connection_db):
            await message.answer("Недостаточно прав")
            return

        if not command.args:
            await message.answer("Неправильный формат текста")
            return

        msg = f"Объявление от {message.from_user.username}:\n"
        msg += command.args

        connection_db.row_factory = lambda cursor, row: row[0]
        c = connection_db.cursor()
        user_ids = c.execute("SELECT userid FROM users").fetchall()
        for userid in user_ids:
            last_msg = await bot.send_message(userid, msg)
            await bot.pin_chat_message(userid, last_msg.message_id)
