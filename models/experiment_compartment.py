import sqlalchemy as sql
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from models.orm_base import OrmBase


class ExperimentCompartment(OrmBase):
    __tablename__ = 'ExperimentCompartments'

    id: Mapped[int] = mapped_column(sql.Integer, primary_key=True)

    studyId: Mapped[str] = mapped_column(sql.ForeignKey('Study.studyId'))

    experimentId:  Mapped[int] = mapped_column(sql.ForeignKey('Experiments.id'))
    compartmentId: Mapped[int] = mapped_column(sql.ForeignKey('Compartments.id'))

    study:       Mapped['Study']       = relationship(back_populates="experimentCompartments")
    experiment:  Mapped['Experiment']  = relationship(back_populates="experimentCompartments")
    compartment: Mapped['Compartment'] = relationship(back_populates="experimentCompartments")
