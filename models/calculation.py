from datetime import datetime

from sqlalchemy import (
    String,
    ForeignKey,
    JSON,
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
    'ready',
    'error',
]


class Calculation(OrmBase):
    __tablename__ = "Calculations"

    id:          Mapped[int] = mapped_column(primary_key=True)
    type:        Mapped[str] = mapped_column(String(100), nullable=False)
    subjectId:   Mapped[str] = mapped_column(String(100), nullable=False)
    subjectType: Mapped[str] = mapped_column(String(100), nullable=False)

    measurementTechniqueId: Mapped[int] = mapped_column(
        ForeignKey('MeasurementTechniques.id'),
        nullable=False,
    )
    measurementTechnique: Mapped['MeasurementTechnique'] = relationship(
        back_populates="calculations",
    )

    calculationTechniqueId: Mapped[int] = mapped_column(
        ForeignKey('CalculationTechniques.id'),
        nullable=False,
    )
    calculationTechnique: Mapped['CalculationTechnique'] = relationship(
        back_populates="calculations",
    )

    coefficients: Mapped[JSON] = mapped_column(JSON, nullable=False)

    state: Mapped[str] = mapped_column(String(100), default='pending')
    error: Mapped[str] = mapped_column(String(100))

    createdAt:    Mapped[datetime] = mapped_column(UtcDateTime, server_default=FetchedValue())
    updatedAt:    Mapped[datetime] = mapped_column(UtcDateTime, server_default=FetchedValue())
    calculatedAt: Mapped[datetime] = mapped_column(UtcDateTime)

    @validates('type')
    def _validate_type(self, key, value):
        return self._validate_inclusion(key, value, VALID_TYPES)

    @validates('state')
    def _validate_state(self, key, value):
        return self._validate_inclusion(key, value, VALID_STATES)
