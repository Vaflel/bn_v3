import os.path

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from config import settings

db_path = os.path.join(settings.DATA_DIRECTORY, "bot.db")
engine = create_async_engine(f"sqlite+aiosqlite:///{db_path}")
new_session = async_sessionmaker(engine, expire_on_commit=False)
