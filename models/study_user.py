from typing import List

from sqlalchemy import (
    String,
    Integer,
    ForeignKey,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from models.orm_base import OrmBase


class StudyUser(OrmBase):
    __tablename__ = 'StudyUsers'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    studyUniqueID: Mapped[str] = mapped_column(ForeignKey('Study.studyUniqueID'), nullable=False)
    userUniqueID:  Mapped[str] = mapped_column(String(100), nullable=False)

    study: Mapped[List['Study']] = relationship(back_populates="studyUsers")
