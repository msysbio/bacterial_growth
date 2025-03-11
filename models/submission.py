import sqlalchemy as sql
from sqlalchemy import String
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)
from sqlalchemy.types import JSON

from models.orm_base import OrmBase


class Submission(OrmBase):
    __tablename__ = 'Submissions'

    id: Mapped[int] = mapped_column(primary_key=True)

    projectUniqueID: Mapped[str] = mapped_column(String(100), nullable=False)
    studyUniqueID:   Mapped[str] = mapped_column(String(100), nullable=False)
    userUniqueID:    Mapped[str] = mapped_column(String(100), nullable=False)

    studyDesign: Mapped[JSON] = mapped_column(JSON, nullable=False)
