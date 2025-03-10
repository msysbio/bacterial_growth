from typing import List

from sqlalchemy import String
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from models.orm_base import OrmBase


class Study(OrmBase):
    __tablename__ = 'Study'

    studyId: Mapped[str] = mapped_column(String(100), primary_key=True)
    studyName: Mapped[str] = mapped_column(String(100), nullable=False)

    experiments: Mapped[List['Experiment']] = relationship(
        back_populates='study',
        cascade="all, delete-orphan"
    )
