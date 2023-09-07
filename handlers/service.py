from aiogram import Router, Bot, F, types
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters.state import StatesGroup, State
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove

from keyboards.reply_keyboard import make_keyboard_row

from database.dbConnectionCM import DatabaseConnection

router = Router()

groups = ["1", "2"]

class Greeting(StatesGroup):
    welcome_state = State()


@router.message(Command("start"))
async def start_command(message: types.Message, state: FSMContext):
    await state.clear()

    with DatabaseConnection() as connection_db:

        user_id = message.from_user.id
        info = connection_db.execute(f'SELECT * FROM users WHERE userid={user_id}')

        if info.fetchone() is None:
            await message.reply(
                text=f"Привет, {message.from_user.first_name}!\nУкажи свою группу:",
                reply_markup=make_keyboard_row(groups)
            )
            await state.set_state(Greeting.welcome_state)
            return

    await message.reply(f"С возвращением, {message.from_user.first_name}!\nПомощь по взаимодействию: /help", reply_markup=ReplyKeyboardRemove())


@router.message(Greeting.welcome_state, F.text.in_(groups))
async def group_chosen(message: types.Message, state: FSMContext):
    with DatabaseConnection() as connection_db:
        user_id = message.from_user.id
        group_num = int(message.text.lower())

        connection_db.execute(
            f"INSERT INTO users (userid, groupnum) VALUES ({user_id}, {group_num})"
        )

        connection_db.commit()

    await message.answer(f""
                         f"Рассылка расписания включена ✅\n"
                         f"Бот высылает расписание на завтра\nв зависимости от числителя/знаменателя, номера группы\n"
                         f"Каждый день 19:00\n\nПомощь по взаимодействию: /help", reply_markup=ReplyKeyboardRemove()
    )
    await state.clear()


@router.message(Greeting.welcome_state)
async def incorrect_group_chosen(message: types.Message):
    await message.answer(
        text="Выбери значение 1 или 2",
        reply_markup=make_keyboard_row(groups)
    )


@router.message(Command("help"))
async def help_command(message: types.Message):
    await message.answer(
        "Команды взаимодействия:\n"
        "/week - расписание на неделю\n"
        "/today - расписание на сегодня\n"
        "/tomorrow - расписание на завтра\n"
        "/group - сменить группу\n"
        "/broadcast - включить/выключить рассылку расписания\n"
        "/message_all [text] - рассылка всем пользователям (super_user)\n\n"
        "Сервисные команды:\n"
        "/start - перезапустить бота\n"
        "/cancel - отменить действие\n"
        "/clear - очистить последние сообщения\n\n"
        "Помощь по взаимодействию: /help\n"
    )


@router.message(Command("clear"))
async def cmd_clear(message: types.Message, bot: Bot) -> None:
    try:
        for i in range(message.message_id, 0, -1):
            await bot.delete_message(message.from_user.id, i)
    except TelegramBadRequest as ex:
        if ex.message == "Bad Request: message to delete not found":
            pass


@router.message(Command("cancel"))
async def cancel_command(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Действие отменено", reply_markup=ReplyKeyboardRemove())
