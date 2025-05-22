from src.core.common.database import new_session
from src.core.users.repository import UsersRepository, ChatsRepository


class SqlAlchemyUnitOfWork:
    users: UsersRepository
    chats: ChatsRepository

    def __init__(self, session_factory=new_session):
        self.session_factory = session_factory

    async def __aenter__(self):
        self.session = self.session_factory()
        self.users = UsersRepository(self.session)
        self.chats = ChatsRepository(self.session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
        else:
            await self.commit()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()

uow = SqlAlchemyUnitOfWork()
