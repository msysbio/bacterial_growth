from typing import List
from decimal import Decimal

import sqlalchemy as sql
from sqlalchemy.orm import (
    mapped_column,
    relationship,
    Mapped,
)

from models.orm_base import OrmBase


class Compartment(OrmBase):
    __tablename__ = "Compartments"

    id:   Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(sql.String(100), nullable=False)

    # Note: convert to studyUniqueID or delete
    studyId: Mapped[str] = mapped_column(sql.ForeignKey('Study.studyId'), nullable=False)
    study: Mapped['Study'] = relationship(back_populates='compartments')

    volume:        Mapped[Decimal] = mapped_column(sql.Numeric(7, 2), nullable=True)
    pressure:      Mapped[Decimal] = mapped_column(sql.Numeric(7, 2), nullable=True)
    stirringSpeed: Mapped[Decimal] = mapped_column(sql.Numeric(7, 2), nullable=True)
    stirringMode:  Mapped[str]     = mapped_column(sql.String(50), nullable=True)

    O2:  Mapped[Decimal] = mapped_column(sql.Numeric(7, 2), nullable=True)
    CO2: Mapped[Decimal] = mapped_column(sql.Numeric(7, 2), nullable=True)
    H2:  Mapped[Decimal] = mapped_column(sql.Numeric(7, 2), nullable=True)
    N2:  Mapped[Decimal] = mapped_column(sql.Numeric(7, 2), nullable=True)

    inoculumConcentration: Mapped[Decimal] = mapped_column(sql.Numeric(20, 3), nullable=True)
    inoculumVolume:        Mapped[Decimal] = mapped_column(sql.Numeric(7, 2), nullable=True)
    initialPh:             Mapped[Decimal] = mapped_column(sql.Numeric(7, 2), nullable=True)
    initialTemperature:    Mapped[Decimal] = mapped_column(sql.Numeric(7, 2), nullable=True)

    carbonSource: Mapped[bool] = mapped_column(sql.Boolean)

    mediumName: Mapped[str]  = mapped_column(sql.String(100), nullable=True)
    mediumUrl:  Mapped[str]  = mapped_column(sql.String(100), nullable=True)

    experimentCompartments: Mapped[List['ExperimentCompartment']] = relationship(back_populates='compartment')
    experiments: Mapped[List['Experiment']] = relationship(
        secondary="ExperimentCompartments",
        viewonly=True
    )

    measurementContexts: Mapped[List['MeasurementContext']] = relationship(back_populates='compartment')
    measurements: Mapped[List['Measurement']] = relationship(
        order_by='Measurement.timeInSeconds',
        secondary='MeasurementContexts',
        viewonly=True,
    )
