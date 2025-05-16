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
from lib.db import execute_into_df

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

    type:  Mapped[str] = mapped_column(sql.String(100), nullable=False)
    units: Mapped[str] = mapped_column(sql.String(100), nullable=False)

    subjectType: Mapped[str] = mapped_column(sql.String(100), nullable=False)

    description: Mapped[str]  = mapped_column(sql.String)
    includeStd:  Mapped[bool] = mapped_column(sql.Boolean, nullable=False, default=False)

    metaboliteIds: Mapped[sql.JSON] = mapped_column(sql.JSON, nullable=False)
    strainIds:     Mapped[sql.JSON] = mapped_column(sql.JSON, nullable=False)

    studyUniqueID: Mapped[str] = mapped_column(sql.ForeignKey('Study.studyUniqueID'), nullable=False)
    study: Mapped['Study'] = relationship(back_populates="measurementTechniques")

    createdAt: Mapped[datetime] = mapped_column(UtcDateTime, server_default=FetchedValue())
    updatedAt: Mapped[datetime] = mapped_column(UtcDateTime, server_default=FetchedValue())

    measurementContexts: Mapped[List['MeasurementContext']] = relationship(
        back_populates="technique",
        order_by='MeasurementContext.bioreplicateId, MeasurementContext.compartmentId',
    )
    measurements: Mapped[List['Measurement']] = relationship(
        secondary='MeasurementContexts',
        viewonly=True,
    )
    calculations: Mapped[List['Calculation']] = relationship(
        back_populates="measurementTechnique"
    )

    @property
    def short_name(self):
        return TECHNIQUE_SHORT_NAMES[self.type]

    @property
    def long_name(self):
        return TECHNIQUE_LONG_NAMES[self.type]

    @property
    def name_with_subject_type(self):
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
        from models import Bioreplicate, Measurement

        return db_session.scalars(
            sql.select(Bioreplicate)
            .distinct()
            .join(Measurement)
            .where(Measurement.techniqueId == self.id)
        ).all()

    def get_subjects_for_bioreplicate(self, db_session, bioreplicate):
        from models import Measurement

        match self.subjectType:
            case 'bioreplicate':
                from models import Bioreplicate
                subject_class = Bioreplicate
            case 'strain':
                from models import Strain
                subject_class = Strain
            case 'metabolite':
                from models import Metabolite
                subject_class = Metabolite

        return db_session.scalars(
            sql.select(subject_class)
            .where(subject_class.id.in_(
                sql.select(Measurement.subjectId)
                .distinct()
                .where(
                    Measurement.techniqueId == self.id,
                    Measurement.bioreplicateUniqueId == bioreplicate.id,
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
            contexts = list([mc for mc in group if mc.has_measurements()])

            yield ((bioreplicate, compartment), contexts)

    def get_subject_df(self, db_session, bioreplicate_uuid, subject_id, subject_type):
        from models import Measurement, MeasurementContext, Bioreplicate

        subjectName, subjectJoin = MeasurementContext.subject_join(subject_type)

        query = (
            sql.select(
                Measurement.timeInHours.label("time"),
                Measurement.value,
                Measurement.std,
                subjectName,
            )
            .join(MeasurementContext)
            .join(Bioreplicate)
            .join(*subjectJoin)
            .where(
                Measurement.contextId == MeasurementContext.id,
                MeasurementContext.techniqueId == self.id,
                MeasurementContext.bioreplicateId == bioreplicate_uuid,
                MeasurementContext.subjectId == subject_id,
                MeasurementContext.subjectType == subject_type,
            )
            .order_by(Measurement.timeInSeconds)
        )

        return execute_into_df(db_session, query)
