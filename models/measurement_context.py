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

from models.orm_base import OrmBase
from lib.conversion import convert_time
from lib.util import group_by_unique_name


class MeasurementContext(OrmBase):
    __tablename__ = "MeasurementContexts"

    id: Mapped[int] = mapped_column(primary_key=True)

    bioreplicateId: Mapped[int] = mapped_column(sql.ForeignKey('Bioreplicates.id'))
    bioreplicate: Mapped['Bioreplicate'] = relationship(back_populates='measurementContexts')

    compartmentId: Mapped[int] = mapped_column(sql.ForeignKey('Compartments.id'))
    compartment: Mapped['Compartment'] = relationship(back_populates='measurementContexts')

    studyId: Mapped[str] = mapped_column(sql.ForeignKey('Study.studyId'), nullable=False)
    study: Mapped['Study'] = relationship(back_populates='measurementContexts')

    techniqueId: Mapped[int] = mapped_column(sql.ForeignKey("MeasurementTechniques.id"))
    technique: Mapped['MeasurementTechnique'] = relationship(
        back_populates="measurementContexts"
    )

    measurements: Mapped[List['Measurement']] = relationship(
        back_populates="context",
        cascade='all, delete-orphan',
    )

    subjectId:   Mapped[str] = mapped_column(sql.String(100), nullable=False)
    subjectType: Mapped[str] = mapped_column(sql.String(100), nullable=False)

    def has_measurements(self):
        return len([m for m in self.measurements if m.value is not None]) > 0

    def get_subject(self, db_session):
        from models import Metabolite, Strain, Bioreplicate

        if self.subjectType == 'metabolite':
            return db_session.get(Metabolite, self.subjectId)
        elif self.subjectType == 'strain':
            return db_session.get(Strain, self.subjectId)
        elif self.subjectType == 'bioreplicate':
            return db_session.get(Bioreplicate, self.subjectId)
        else:
            raise ValueError(f"Unknown subject type: {self.subjectType}")

    def subject_join(subject_type):
        from models import Metabolite, Strain, Bioreplicate

        if subject_type == 'metabolite':
            Subject = Metabolite
        elif subject_type == 'strain':
            Subject = Strain
        elif subject_type == 'bioreplicate':
            Subject = aliased(Bioreplicate)

        name = Subject.name.label("subjectName")
        join = (Subject, MeasurementContext.subjectId == Subject.id)

        return (name, join)
