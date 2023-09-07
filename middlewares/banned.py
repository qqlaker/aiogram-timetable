from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Update

from database.dbConnectionCM import DatabaseConnection


def _is_banned(user_id: int) -> bool:
    with DatabaseConnection() as connection_db:
        row = connection_db.execute(f"SELECT * FROM users WHERE userid = {user_id}").fetchone()
        if row is not None:
            return bool(row[2])
    return 0

class BannedUpdateMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: Dict[str, Any]
    ) -> Any:
        if not _is_banned(data["event_from_user"].id):
            return await handler(event, data)
        await event.message.answer("Доступ запрещён")