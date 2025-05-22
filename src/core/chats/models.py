from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.core.common.models import Model



class ChatsOrm(Model):
    __tablename__ = "chats"

    chat_id: Mapped[int] = mapped_column(primary_key=True)
    group_name: Mapped[str]
    department_name: Mapped[str]
