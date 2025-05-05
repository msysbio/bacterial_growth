from typing import List

import sqlalchemy as sql
from sqlalchemy import (
    String,
    ForeignKey,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy.ext.hybrid import hybrid_property

from models.orm_base import OrmBase


class Experiment(OrmBase):
    __tablename__ = "Experiments"

    id: Mapped[int] = mapped_column(primary_key=True)

    name:        Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String)

    bioreplicates: Mapped[List['Bioreplicate']] = relationship(
        order_by="Bioreplicate.id",
        back_populates='experiment',
        cascade="all, delete-orphan"
    )

    communityId: Mapped[int] = mapped_column(ForeignKey('Communities.id'))
    community: Mapped['Community'] = relationship(back_populates='experiments')

    studyId: Mapped[str] = mapped_column(ForeignKey('Study'), nullable=False)
    study: Mapped['Study'] = relationship(back_populates='experiments')

    cultivationMode: Mapped[str] = mapped_column(String(50))

    experimentCompartments: Mapped[List['ExperimentCompartment']] = relationship(back_populates='experiment')
    compartments: Mapped[List['Compartment']] = relationship(
        secondary='ExperimentCompartments',
        viewonly=True,
    )

    @property
    def measurements(self):
        for bioreplicate in self.bioreplicates:
            for measurement in bioreplicate.measurements:
                yield measurement
