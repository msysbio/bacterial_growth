from typing import List

import sqlalchemy as sql
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.model.orm.orm_base import OrmBase


class Experiment(OrmBase):
    __tablename__ = "Experiments"

    id: Mapped[int] = mapped_column(primary_key=True)

    name:        Mapped[str] = mapped_column(sql.String(100), nullable=False)
    description: Mapped[str] = mapped_column(sql.String)

    bioreplicates: Mapped[List['Bioreplicate']] = relationship(
        order_by="Bioreplicate.id",
        back_populates='experiment',
        cascade="all, delete-orphan"
    )

    communityId: Mapped[int] = mapped_column(sql.ForeignKey('Communities.id'))
    community: Mapped['Community'] = relationship(back_populates='experiments')

    studyId: Mapped[str] = mapped_column(sql.ForeignKey('Study'), nullable=False)
    study: Mapped['Study'] = relationship(back_populates='experiments')

    cultivationMode: Mapped[str] = mapped_column(sql.String(50))

    experimentCompartments: Mapped[List['ExperimentCompartment']] = relationship(back_populates='experiment')
    compartments: Mapped[List['Compartment']] = relationship(
        secondary='ExperimentCompartments',
        viewonly=True,
    )

    perturbations: Mapped[List['Perturbation']] = relationship(back_populates='experiment')

    measurementContexts: Mapped[List['MeasurementContext']] = relationship(
        secondary='Bioreplicates',
        viewonly=True,
    )
