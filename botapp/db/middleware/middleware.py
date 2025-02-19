from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from ..database.database import get_async_session, session_maker


class DBMiddleware(BaseMiddleware):
    async def __call__(
        self,
        hanlder: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        async with session_maker() as session:
            self.set_session(data, session)
            try:
                result = await hanlder(event, data)
                await self.after_handler(session)
                return result
            except Exception as e:
                await session.rollback()
                raise e
            finally:
                await session.close()

    def set_session(self, data: Dict[str, Any], session) -> None:
        raise NotImplementedError("Этот метод должен быть реализован в подклассах.")

    async def after_handler(self, session) -> None:
        pass

class DBMiddlewareWithComm(DBMiddleware):
    def set_session(self, data: Dict[str, Any], session) -> None:
        data['session_with_commit'] = session

    async def after_handler(self, session) -> None:
        print("commit")
        await session.commit()


class DBMiddlewareWithoutComm(DBMiddleware):
    def set_session(self, data: Dict[str, Any], session) -> None:
        data['session_without_commit'] = session

