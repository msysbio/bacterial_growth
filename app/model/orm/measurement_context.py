import csv
from typing import List
from io import StringIO
from decimal import Decimal

import sqlalchemy as sql
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
    aliased,
)
from sqlalchemy.ext.hybrid import hybrid_property

from app.model.orm.orm_base import OrmBase
from app.model.lib.db import execute_into_df
from app.model.lib.conversion import convert_time
from app.model.lib.util import group_by_unique_name


class MeasurementContext(OrmBase):
    __tablename__ = "MeasurementContexts"

    id: Mapped[int] = mapped_column(primary_key=True)

    bioreplicateId: Mapped[int] = mapped_column(sql.ForeignKey('Bioreplicates.id'))
    bioreplicate: Mapped['Bioreplicate'] = relationship(back_populates='measurementContexts')

    compartmentId: Mapped[int] = mapped_column(sql.ForeignKey('Compartments.id'))
    compartment: Mapped['Compartment'] = relationship(back_populates='measurementContexts')

    studyId: Mapped[str] = mapped_column(sql.ForeignKey('Studies.studyId'), nullable=False)
    study: Mapped['Study'] = relationship(back_populates='measurementContexts')

    techniqueId: Mapped[int] = mapped_column(sql.ForeignKey("MeasurementTechniques.id"))
    technique: Mapped['MeasurementTechnique'] = relationship(
        back_populates='measurementContexts'
    )

    measurements: Mapped[List['Measurement']] = relationship(
        back_populates='context',
        cascade='all, delete-orphan',
    )
    modelingResults: Mapped[List['ModelingResult']] = relationship(
        back_populates='measurementContext',
        cascade='all, delete-orphan',
    )

    calculationType: Mapped[str] = mapped_column(sql.String(50))

    subjectId:   Mapped[str] = mapped_column(sql.String(100), nullable=False)
    subjectType: Mapped[str] = mapped_column(sql.String(100), nullable=False)

    def get_df(self, db_session):
        from app.model.orm import Measurement

        query = (
            sql.select(
                Measurement.timeInHours.label("time"),
                Measurement.value,
                Measurement.std,
            )
            .join(MeasurementContext)
            .where(
                MeasurementContext.id == self.id,
                Measurement.value.is_not(None),
            )
            .order_by(Measurement.timeInSeconds)
        )

        return execute_into_df(db_session, query)

    def get_chart_label(self, db_session):
        subject      = self.get_subject(db_session)
        technique    = self.technique
        bioreplicate = self.bioreplicate
        compartment  = self.compartment

        if technique.subjectType == 'metabolite':
            label_parts = [f"<b>{subject.name}</b>"]
        else:
            label_parts = [technique.short_name]

        if technique.subjectType == 'bioreplicate':
            label_parts.append('of the')
            label_parts.append(f"<b>{subject.name}<sub>{compartment.name}</sub></b>")
            label_parts.append('community')
        elif technique.subjectType == 'metabolite':
            label_parts.append('in')
            label_parts.append(f"{bioreplicate.name}<sub>{compartment.name}</sub>")
        else:
            label_parts.append('of')
            label_parts.append(f"<b>{subject.name}</b>")
            label_parts.append('in')
            label_parts.append(f"{bioreplicate.name}<sub>{compartment.name}</sub>")

        label = ' '.join(label_parts)

        return label

    def get_subject(self, db_session):
        from app.model.orm import Metabolite, Strain, Bioreplicate

        if self.subjectType == 'metabolite':
            return db_session.scalars(
                sql.select(Metabolite)
                .where(Metabolite.chebiId == self.subjectId)
                .limit(1)
            ).one_or_none()
        elif self.subjectType == 'strain':
            return db_session.get(Strain, self.subjectId)
        elif self.subjectType == 'bioreplicate':
            return db_session.get(Bioreplicate, self.subjectId)
        else:
            raise ValueError(f"Unknown subject type: {self.subjectType}")
