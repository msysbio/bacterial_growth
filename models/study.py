from sqlalchemy import String
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from models.orm_base import OrmBase


class Study(OrmBase):
    __tablename__ = 'Study'

    studyId: Mapped[str] = mapped_column(String(100), primary_key=True)
    studyName: Mapped[str] = mapped_column(String(100), nullable=False)
