from sqlalchemy import (
    String,
    Integer,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from models.orm_base import OrmBase


class StudyUser(OrmBase):
    __tablename__ = 'StudyUsers'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    studyUniqueID: Mapped[str] = mapped_column(String(100), nullable=False)
    userUniqueID:  Mapped[str] = mapped_column(String(100), nullable=False)
