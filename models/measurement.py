import enum
from decimal import Decimal

from sqlalchemy import (
    Enum,
    ForeignKey,
    Integer,
    String,
    Numeric,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from models.orm_base import OrmBase

class Measurement(OrmBase):
    __tablename__ = "Measurements"

    class SubjectType(enum.Enum):
        metabolite   = 'metabolite'
        strain       = 'strain'
        bioreplicate = 'bioreplicate'

    id: Mapped[int] = mapped_column(primary_key=True)

    # Note: should be a ForeignKey + relationship. However, ORM model is not
    # defined yet.
    bioreplicateUniqueId: Mapped[int] = mapped_column(Integer, nullable=False)

    position:      Mapped[str] = mapped_column(String(100), nullable=False)
    timeInSeconds: Mapped[int] = mapped_column(Integer,     nullable=False)
    pH:            Mapped[str] = mapped_column(String(100), nullable=False)
    unit:          Mapped[str] = mapped_column(String(100), nullable=False)

    # TODO (2025-02-13) Consider an enum
    technique: Mapped[str] = mapped_column(String(100), nullable=False)

    absoluteValue: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=True)
    relativeValue: Mapped[Decimal] = mapped_column(Numeric(10, 9), nullable=True)

    subjectType: Mapped[str] = mapped_column(Enum(SubjectType), nullable=False)
    subjectId:   Mapped[str] = mapped_column(String(100),       nullable=False)
