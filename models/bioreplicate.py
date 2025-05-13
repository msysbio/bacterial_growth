from typing import List

import sqlalchemy as sql
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy.ext.hybrid import hybrid_property

from models.orm_base import OrmBase
from lib.db import execute_text


class Bioreplicate(OrmBase):
    __tablename__ = 'Bioreplicates'

    id:   Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(sql.String(100), nullable=False)

    position:     Mapped[str] = mapped_column(sql.String(100))
    biosampleUrl: Mapped[str] = mapped_column(sql.String)

    isControl: Mapped[bool] = mapped_column(sql.Boolean, nullable=False, default=False)
    isBlank:   Mapped[bool] = mapped_column(sql.Boolean, nullable=False, default=False)

    studyId: Mapped[str] = mapped_column(sql.ForeignKey('Study.studyId'), nullable=False)
    study: Mapped['Study'] = relationship(back_populates='bioreplicates')

    experimentId: Mapped[int] = mapped_column(sql.ForeignKey('Experiments.id'), nullable=False)
    experiment: Mapped['Experiment'] = relationship(back_populates='bioreplicates')

    measurements: Mapped[List["Measurement"]] = relationship(
        order_by='Measurement.timeInSeconds',
        back_populates='bioreplicate',
        cascade='all, delete-orphan'
    )
    calculations: Mapped[List["Calculation"]] = relationship(
        back_populates='bioreplicate',
        cascade='all, delete-orphan'
    )

    @staticmethod
    def find_for_study(db_session, study_id, name):
        return db_session.scalars(
            sql.select(Bioreplicate.id)
            .where(
                Bioreplicate.studyId == study_id,
                Bioreplicate.name == name,
            )
        ).one()
