from datetime import datetime
from typing import List

import sqlalchemy as sql
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
    validates,
)
from sqlalchemy.schema import FetchedValue
from sqlalchemy_utc.sqltypes import UtcDateTime

from models.orm_base import OrmBase

VALID_TYPES = [
    'easy_linear',
    'baranyi_roberts',
]

VALID_STATES = [
    'pending',
    'in_progress',
    'ready',
    'error',
]

MODEL_NAMES = {
    'easy_linear':     'Easy linear model',
    'baranyi_roberts': 'Baranyi-Roberts model',
}


class CalculationTechnique(OrmBase):
    __tablename__ = "CalculationTechniques"

    id:   Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(sql.String(100), nullable=False)

    studyUniqueID: Mapped[str] = mapped_column(sql.ForeignKey('Study.studyUniqueID'), nullable=False)
    study: Mapped['Study'] = relationship(back_populates="calculationTechniques")

    jobUuid: Mapped[str] = mapped_column(sql.String(100))
    state:   Mapped[str] = mapped_column(sql.String(100), default='pending')
    error:   Mapped[str] = mapped_column(sql.String(100))

    createdAt: Mapped[datetime] = mapped_column(UtcDateTime, server_default=FetchedValue())
    updatedAt: Mapped[datetime] = mapped_column(UtcDateTime, server_default=FetchedValue())

    calculations: Mapped[List['Calculation']] = relationship(
        back_populates="calculationTechnique",
        cascade="all, delete-orphan"
    )

    @validates('type')
    def _validate_type(self, key, value):
        return self._validate_inclusion(key, value, VALID_TYPES)

    @validates('state')
    def _validate_state(self, key, value):
        return self._validate_inclusion(key, value, VALID_STATES)

    @property
    def long_name(self):
        return MODEL_NAMES[self.type]
