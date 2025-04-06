from datetime import datetime
from typing import List
import itertools

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

TECHNIQUE_SHORT_NAMES = {
    'ph':         'pH',
    'fc':         'FC',
    'od':         'OD',
    'plates':     'PC',
    '16s':        '16S-rRNA reads',
    'metabolite': 'Metabolite',
}

TECHNIQUE_LONG_NAMES = {
    'ph':         'pH',
    'fc':         'Flow Cytometry',
    'od':         'Optical Density',
    'plates':     'Plate Counts',
    '16s':        '16S-rRNA reads',
    'metabolite': 'Metabolites',
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

    measurements: Mapped[List['Measurement']] = relationship(
        back_populates="techniqueRecord"
    )

    @property
    def short_name(self):
        return TECHNIQUE_SHORT_NAMES[self.type]

    @property
    def long_name(self):
        return TECHNIQUE_LONG_NAMES[self.type]

    @property
    def subject_short_name(self):
        match self.subjectType:
            case 'bioreplicate': return 'community'
            case 'strain': return 'strain'
            case 'metabolite': return 'metabolite'

    def csv_column_name(self, subject_name=None):
        if self.subjectType == 'bioreplicate':
            return f"Community {TECHNIQUE_SHORT_NAMES[self.type]}"

        elif self.subjectType == 'metabolite':
            return subject_name

        elif self.subjectType == 'strain':
            if self.type == '16s':
                suffix = 'rRNA reads'
            elif self.type == 'fc':
                suffix = 'FC counts'
            elif self.type == 'plates':
                suffix = 'plate counts'
            else:
                raise ValueError(f"Incompatible type and subjectType: {self.type}, {self.subjectType}")

            return f"{subject_name} {suffix}"

    def measurements_by_subject(self, db_session):
        from models import Measurement

        grouper = lambda m: (m.subjectType, m.subjectId)

        ordered_measurements = sorted(self.measurements, key=grouper)
        for ((subject_type, subject_id), group) in itertools.groupby(ordered_measurements, grouper):
            subject = Measurement.get_subject(db_session, subject_id, subject_type)

            yield (subject, list(group))
