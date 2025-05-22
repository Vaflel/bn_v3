from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.core.common.models import Model


class UsersOrm(Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    group_name: Mapped[str]
    department_name: Mapped[str]
    is_admin: Mapped[bool]


