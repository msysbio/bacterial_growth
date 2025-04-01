from datetime import datetime

from sqlalchemy import (
    String,
    Boolean,
    ForeignKey,
    JSON,
    DateTime,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy.schema import FetchedValue
from sqlalchemy.ext.hybrid import hybrid_property

from models.orm_base import OrmBase

TECHNIQUE_NAMES = {
    'ph':     'pH',
    'fc':     'FC',
    'od':     'OD',
    'plates': 'PC',
    '16s':    '16S-rRNA reads',
}


class MeasurementTechnique(OrmBase):
    __tablename__ = "MeasurementTechniques"

    id: Mapped[int] = mapped_column(primary_key=True)

    type:  Mapped[str] = mapped_column(String(100), nullable=False)
    units: Mapped[str] = mapped_column(String(100), nullable=False)

    subjectType: Mapped[str] = mapped_column(String(100), nullable=False)

    description: Mapped[str]  = mapped_column(String)
    includeStd:  Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    metaboliteIds: Mapped[JSON] = mapped_column(JSON, nullable=False)
    strainIds:     Mapped[JSON] = mapped_column(JSON, nullable=False)

    studyUniqueID: Mapped[str] = mapped_column(ForeignKey('Study.studyUniqueID'), nullable=False)
    study: Mapped['Study'] = relationship(back_populates="measurementTechniques")

    createdAt: Mapped[datetime] = mapped_column(DateTime, server_default=FetchedValue())
    updatedAt: Mapped[datetime] = mapped_column(DateTime, server_default=FetchedValue())
