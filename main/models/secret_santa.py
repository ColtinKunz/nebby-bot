from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main.models import User

from sqlalchemy import ForeignKey, String, Boolean
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from .core import Base, BaseTable


class SecretSantaAssignment(BaseTable):
    __tablename__ = "secret_santa_assignment_table"
    to_user_id: Mapped[int] = mapped_column(ForeignKey("user_table.id"))
    from_user_id: Mapped[int] = mapped_column(ForeignKey("user_table.id"))
    secret_santa_event_id: Mapped[int] = mapped_column(
        ForeignKey("secret_santa_event_table.id")
    )

    from_user: Mapped[User] = relationship(
        "User",
        back_populates="secret_santa_assignments",
        foreign_keys=[from_user_id],
    )
    to_user: Mapped[User] = relationship(
        "User",
        back_populates="secret_santa_assignees",
        foreign_keys=[to_user_id],
    )
    secret_santa_event: Mapped["SecretSantaEvent"] = relationship(
        "SecretSantaEvent",
        back_populates="secret_santa_assignments",
        foreign_keys=[secret_santa_event_id],
    )


class SecretSantaEvent(BaseTable):
    __tablename__ = "secret_santa_event_table"
    name: Mapped[str] = mapped_column(String())
    ongoing: Mapped[bool] = mapped_column(Boolean())

    previous_event_id: Mapped[int] = mapped_column(
        ForeignKey("secret_santa_event_table.id"), nullable=True
    )
    previous_event: Mapped["SecretSantaEvent"] = relationship(
        "SecretSantaEvent",
        foreign_keys=[previous_event_id],
    )

    owner_id: Mapped[int] = mapped_column(ForeignKey("user_table.id"))
    owner: Mapped["User"] = relationship(
        "User",
        back_populates="owned_secret_santa_events",
        foreign_keys=[owner_id],
    )

    users: Mapped[list["User"]] = relationship(
        secondary="user_secret_santa_event_mapping_table",
        back_populates="secret_santa_events",
        viewonly=True,
    )
    user_associations: Mapped[list["UserSecretSantaEvent"]] = relationship(
        back_populates="secret_santa_event"
    )

    secret_santa_assignments: Mapped[
        list["SecretSantaAssignment"]
    ] = relationship(
        "SecretSantaAssignment",
        back_populates="secret_santa_event",
    )

    def __repr__(self) -> str:
        users = "\n".join([f"\t{user.name}" for user in self.users])
        return f"ID:{self.id!r}\nPrevious Event: {self.previous_event.name if self.previous_event else None}\n\n{users}"


class UserSecretSantaEvent(Base):
    __tablename__ = "user_secret_santa_event_mapping_table"
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user_table.id"), primary_key=True
    )
    secret_santa_event_id: Mapped[int] = mapped_column(
        ForeignKey("secret_santa_event_table.id"), primary_key=True
    )
    user: Mapped[User] = relationship(
        back_populates="secret_santa_event_associations"
    )
    secret_santa_event: Mapped["SecretSantaEvent"] = relationship(
        back_populates="user_associations"
    )
