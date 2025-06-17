from datetime import datetime
from typing import List
import itertools

import sqlalchemy as sql
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy.schema import FetchedValue
from sqlalchemy_utc.sqltypes import UtcDateTime

from app.model.orm.orm_base import OrmBase

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

    type:  Mapped[str] = mapped_column(sql.String(100), nullable=False)
    units: Mapped[str] = mapped_column(sql.String(100), nullable=False)

    subjectType: Mapped[str] = mapped_column(sql.String(100), nullable=False)

    description: Mapped[str]  = mapped_column(sql.String)
    includeStd:  Mapped[bool] = mapped_column(sql.Boolean, nullable=False, default=False)

    metaboliteIds: Mapped[sql.JSON] = mapped_column(sql.JSON, nullable=False)
    strainIds:     Mapped[sql.JSON] = mapped_column(sql.JSON, nullable=False)

    studyUniqueID: Mapped[str] = mapped_column(sql.ForeignKey('Studies.studyUniqueID'), nullable=False)
    study: Mapped['Study'] = relationship(back_populates="measurementTechniques")

    createdAt: Mapped[datetime] = mapped_column(UtcDateTime, server_default=FetchedValue())
    updatedAt: Mapped[datetime] = mapped_column(UtcDateTime, server_default=FetchedValue())

    measurementContexts: Mapped[List['MeasurementContext']] = relationship(
        back_populates="technique",
        order_by='MeasurementContext.calculationType.is_(None), MeasurementContext.bioreplicateId, MeasurementContext.compartmentId',
    )
    measurements: Mapped[List['Measurement']] = relationship(
        secondary='MeasurementContexts',
        viewonly=True,
    )

    def __lt__(self, other):
        return self.id < other.id

    @property
    def short_name(self):
        return TECHNIQUE_SHORT_NAMES[self.type]

    @property
    def long_name(self):
        return TECHNIQUE_LONG_NAMES[self.type]

    @property
    def long_name_with_subject_type(self):
        parts = [self.long_name]

        if self.subjectType != 'metabolite':
            parts.append(self.subject_short_name)

        return ' per '.join(parts)

    @property
    def subject_short_name(self):
        match self.subjectType:
            case 'bioreplicate': return 'community'
            case 'strain': return 'strain'
            case 'metabolite': return 'metabolite'

    @property
    def is_growth(self):
        return self.type not in ('ph', 'metabolite')

    def get_bioreplicates(self, db_session):
        from app.model.orm import Bioreplicate, MeasurementContext

        return db_session.scalars(
            sql.select(Bioreplicate)
            .distinct()
            .join(MeasurementContext)
            .where(MeasurementContext.techniqueId == self.id)
        ).all()

    def get_subjects_for_bioreplicate(self, db_session, bioreplicate):
        from app.model.orm import MeasurementContext, Measurement

        match self.subjectType:
            case 'bioreplicate':
                from app.model.orm import Bioreplicate
                subject_class = Bioreplicate
            case 'strain':
                from app.model.orm import Strain
                subject_class = Strain
            case 'metabolite':
                from app.model.orm import Metabolite
                subject_class = Metabolite

        return db_session.scalars(
            sql.select(subject_class)
            .where(subject_class.id.in_(
                sql.select(MeasurementContext.subjectId)
                .join(Measurement)
                .distinct()
                .where(
                    MeasurementContext.techniqueId == self.id,
                    MeasurementContext.bioreplicateId == bioreplicate.id,
                    Measurement.value.is_not(None),
                )
            ))
        ).all()

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

    def get_grouped_contexts(self):
        grouper = lambda mc: (mc.bioreplicate, mc.compartment)

        for ((bioreplicate, compartment), group) in itertools.groupby(self.measurementContexts, grouper):
            contexts = list(group)

            yield ((bioreplicate, compartment), contexts)

    def __str__(self):
        return f"<MeasurementTechnique type={self.type}, id={self.id}>"
