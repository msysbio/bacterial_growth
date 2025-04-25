from datetime import datetime
from typing import List

from sqlalchemy import (
    String,
    ForeignKey,
)
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
    'baranyi_roberts',
]

VALID_STATES = [
    'pending',
    'in_progress',
    'ready',
]


class CalculationTechnique(OrmBase):
    __tablename__ = "CalculationTechniques"

    id:   Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(String(100), nullable=False)

    studyUniqueID: Mapped[str] = mapped_column(ForeignKey('Study.studyUniqueID'), nullable=False)
    study: Mapped['Study'] = relationship(back_populates="calculationTechniques")

    jobUuid: Mapped[str] = mapped_column(String(100))
    state:   Mapped[str] = mapped_column(String(100), default='pending')

    createdAt: Mapped[datetime] = mapped_column(UtcDateTime, server_default=FetchedValue())
    updatedAt: Mapped[datetime] = mapped_column(UtcDateTime, server_default=FetchedValue())

    calculations: Mapped[List['Calculation']] = relationship(
        back_populates="calculationTechnique"
    )

    @validates('type')
    def _validate_type(self, key, value):
        return self._validate_inclusion(key, value, VALID_TYPES)

    @validates('state')
    def _validate_state(self, key, value):
        return self._validate_inclusion(key, value, VALID_STATES)
