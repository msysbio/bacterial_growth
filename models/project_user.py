from sqlalchemy import (
    String,
    Integer,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from models.orm_base import OrmBase


class ProjectUser(OrmBase):
    __tablename__ = 'ProjectUsers'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    projectUniqueID: Mapped[str] = mapped_column(String(100), nullable=False)
    userUniqueID:    Mapped[str] = mapped_column(String(100), nullable=False)
