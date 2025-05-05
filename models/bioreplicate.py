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
    __tablename__ = 'BioReplicatesPerExperiment'

    bioreplicateUniqueId: Mapped[int] = mapped_column(primary_key=True)
    bioreplicateId:       Mapped[str] = mapped_column(sql.String(100), nullable=False)

    studyId: Mapped[str] = mapped_column(sql.ForeignKey('Study.studyId'), nullable=False)
    study: Mapped['Study'] = relationship(back_populates='bioreplicates')

    experimentId: Mapped[str] = mapped_column(sql.String(100), nullable=False)

    experimentUniqueId: Mapped[int] = mapped_column(sql.ForeignKey('Experiments.id'), nullable=False)
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

    @hybrid_property
    def id(self):
        return self.bioreplicateUniqueId

    @hybrid_property
    def uuid(self):
        return self.bioreplicateUniqueId

    @hybrid_property
    def name(self):
        return self.bioreplicateId

    @staticmethod
    def find_for_study(db_conn, study_id, bioreplicate_id):
        return execute_text(db_conn, """
            SELECT bioreplicateUniqueId
            FROM BioReplicatesPerExperiment
            WHERE studyId = :study_id
              AND bioreplicateId = :bioreplicate_id
        """, study_id=study_id, bioreplicate_id=bioreplicate_id).scalar()
