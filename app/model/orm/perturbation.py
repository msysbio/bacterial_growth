import sqlalchemy as sql
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.model.orm.orm_base import OrmBase


class Perturbation(OrmBase):
    __tablename__ = 'Perturbations'

    id:          Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column(sql.String)

    studyId: Mapped[str] = mapped_column(sql.ForeignKey('Studies.studyId'), nullable=False)
    study: Mapped['Study'] = relationship(back_populates='perturbations')

    experimentId: Mapped[int] = mapped_column(sql.ForeignKey('Experiments.id'), nullable=False)
    experiment: Mapped['Experiment'] = relationship(back_populates='perturbations')

    startTimepoint: Mapped[int] = mapped_column(sql.Integer, nullable=False)

    removedCompartmentId: Mapped[int] = mapped_column(sql.ForeignKey('Compartments.id'))
    addedCompartmentId:   Mapped[int] = mapped_column(sql.ForeignKey('Compartments.id'))

    oldCommunityId: Mapped[int] = mapped_column(sql.ForeignKey('Communities.id'))
    newCommunityId: Mapped[int] = mapped_column(sql.ForeignKey('Communities.id'))
