from typing import List
from decimal import Decimal

import sqlalchemy as sql
from sqlalchemy.orm import (
    mapped_column,
    relationship,
    Mapped,
)

from app.model.orm.orm_base import OrmBase


class Compartment(OrmBase):
    __tablename__ = "Compartments"

    id:   Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(sql.String(100), nullable=False)

    # Note: convert to studyUniqueID or delete
    studyId: Mapped[str] = mapped_column(sql.ForeignKey('Studies.studyId'), nullable=False)
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

    @property
    def properties_description(self):
        properties = {
            "volume":                 (self.volume, 'mL'),
            "pressure":               (self.pressure, 'atm'),
            "stirring mode":          (self.stirringMode, ''),
            "stirring speed":         (self.stirringSpeed, 'rpm'),
            "O<sub>2</sub>":          (self.O2, '%'),
            "CO<sub>2</sub>":         (self.CO2, '%'),
            "H<sub>2</sub>":          (self.H2, '%'),
            "N<sub>2</sub>":          (self.N2, '%'),
            "inoculum concentration": (self.inoculumConcentration, ' Cells/mL'),
            "inoculum volume":        (self.inoculumVolume, ' mL'),
            "initial pH":             (self.initialPh, ''),
            "initial temperature":    (self.initialTemperature, '°C'),
        }

        formatted_properties = [
            f"<strong>{v}{units}</strong> {k}"
            for (k, (v, units)) in properties.items()
            if v is not None and v != ''
        ]

        return ', '.join(formatted_properties)
