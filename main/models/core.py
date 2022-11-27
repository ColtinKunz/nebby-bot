from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main.models import (
        UserSecretSantaEvent,
        SecretSantaAssignment,
        SecretSantaEvent,
    )

from sqlalchemy import String, Boolean
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy.sql import expression


SWAP_PREFERENCES = {
    "none": "None",
    "req": "Request",
    "any": "Any",
}


class Base(DeclarativeBase):
    pass


class BaseTable(Base):
    __abstract__ = True
    id: Mapped[int] = mapped_column(primary_key=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean, server_default=expression.true()
    )


class User(BaseTable):

    __tablename__ = "user_table"
    discord_user_id: Mapped[str] = mapped_column(String(17))
    discord_server_id: Mapped[str] = mapped_column(String(17))
    name: Mapped[str] = mapped_column(String)
    owned_secret_santa_events: Mapped[list["SecretSantaEvent"]] = relationship(
        "SecretSantaEvent",
        back_populates="owner",
        foreign_keys="[SecretSantaEvent.owner_id]",
    )
    secret_santa_events: Mapped[list["SecretSantaEvent"]] = relationship(
        secondary="user_secret_santa_event_mapping_table",
        back_populates="users",
        viewonly=True,
    )
    secret_santa_event_associations: Mapped[
        list["UserSecretSantaEvent"]
    ] = relationship(back_populates="user")

    secret_santa_assignments: Mapped[
        list[SecretSantaAssignment]
    ] = relationship(
        "SecretSantaAssignment",
        back_populates="from_user",
        foreign_keys="[SecretSantaAssignment.from_user_id]",
    )
    secret_santa_assignees: Mapped[list[SecretSantaAssignment]] = relationship(
        "SecretSantaAssignment",
        back_populates="to_user",
        foreign_keys="[SecretSantaAssignment.to_user_id]",
    )

    def __repr__(self) -> str:
        return f"User(id={self.id!r})"
