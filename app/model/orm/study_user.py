from typing import List

import sqlalchemy as sql
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.model.orm.orm_base import OrmBase


class StudyUser(OrmBase):
    __tablename__ = 'StudyUsers'

    id: Mapped[int] = mapped_column(sql.Integer, primary_key=True)

    studyUniqueID: Mapped[str] = mapped_column(sql.ForeignKey('Studies.studyUniqueID'), nullable=False)
    userUniqueID:  Mapped[str] = mapped_column(sql.ForeignKey('Users.uuid'),            nullable=False)

    study: Mapped['Study'] = relationship(back_populates="studyUsers")
    user:  Mapped['User']  = relationship(back_populates="studyUsers")
