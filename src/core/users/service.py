from src.core.users.schemas import SUser, SGroupChat
from src.core.common.uow import uow


class UserIsExist(Exception):
    pass


class UserIsNotExist(Exception):
    pass


class UsersService:
    @staticmethod
    async def create_user(user_dto: SUser):
        async with uow:
            if await uow.users.get_by_id(user_dto.id):
                raise UserIsExist
            uow.users.create(user_dto)

    @staticmethod
    async def get_by_id(user_id: int):
        async with uow:
            user_dto = await uow.users.get_by_id(user_id)  # Await the call here
            if user_dto:
                return user_dto
            return None

    @staticmethod
    async def delete_user(user_id: int):
        async with uow:
            user = await uow.users.get_by_id(user_id)
            if user:
                await uow.users.delete(user_id)
            else:
                raise UserIsNotExist("Пользователь не существует.")


class ChatsService:
    @staticmethod
    async def create_chat(chat: SGroupChat):
        async with uow:
            if await uow.chats.get_by_id(chat.chat_id):
                raise UserIsExist
            await uow.chats.create(chat)

    @staticmethod
    async def get_by_id(chat_id: int):
        async with uow:
            chat_dto = await uow.chats.get_by_id(chat_id)
            if chat_dto:
                return chat_dto
            else:
                return None

    @staticmethod
    async def get_list() -> list[SGroupChat]:
        async with uow:
            chats_dto = await uow.chats.get_list()
            return chats_dto

    @staticmethod
    async def delete_chat(chat_id: int):
        async with uow:
            chat = await uow.chats.get_by_id(chat_id)
            if chat:
                await uow.chats.delete(chat_id)
            else:
                raise UserIsNotExist
