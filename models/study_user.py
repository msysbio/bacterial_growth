from typing import List

import sqlalchemy as sql
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from models.orm_base import OrmBase


class StudyUser(OrmBase):
    __tablename__ = 'StudyUsers'

    id: Mapped[int] = mapped_column(sql.Integer, primary_key=True)

    studyUniqueID: Mapped[str] = mapped_column(sql.ForeignKey('Study.studyUniqueID'), nullable=False)
    userUniqueID:  Mapped[str] = mapped_column(sql.String(100), nullable=False)

    study: Mapped[List['Study']] = relationship(back_populates="studyUsers")
