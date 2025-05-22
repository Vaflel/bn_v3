from sqlalchemy.ext.asyncio import AsyncSession

from src.core.users.models import UsersOrm
from src.core.users.schemas import SUser, SGroupChat


class UsersRepository:
    def __init__(self, session):
        self._session: AsyncSession = session

    def create(self, user_dto: SUser):
        user_orm = UsersOrm(**user_dto.model_dump())
        self._session.add(user_orm)

    async def get_by_id(self, id: int):  # Make this method async
        user_orm = await self._session.get(UsersOrm, id)  # Await the get call
        if user_orm:
            user_dto = SUser.model_validate(user_orm)
            return user_dto
        return None

    async def delete(self, id: int):
        user_orm = await self._session.get(UsersOrm, id)
        if user_orm:
            await self._session.delete(user_orm)
        else:
            return None


class ChatsRepository:
    def __init__(self, session):
        self._session: AsyncSession = session

    async  def create(self, chat_dto: SGroupChat):
        chat_orm = ChatsOrm(**chat_dto.model_dump())
        self._session.add(chat_orm)

    async def get_by_id(self, id: int):  # Make this method async
        chats_orm = await self._session.get(ChatsOrm, id)  # Await the get call
        if chats_orm:
            chats_dto = SGroupChat.model_validate(chats_orm)
            return chats_dto
        return None

    async def get_list(self) -> list[SGroupChat]:
        chats_orm = await self._session.get(ChatsOrm)
        chats = []
        for chat_orm in chats_orm:
            chat_dto = SGroupChat.model_validate(chat_orm)
            chats.append(chat_dto)
        return chats

    async def delete(self, id: int):
        chat_orm = await self._session.get(ChatsOrm, id)
        if chat_orm:
            await self._session.delete(chat_orm)
        else:
            return None

