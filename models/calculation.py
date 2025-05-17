from datetime import datetime

import numpy as np
import pandas as pd
import sqlalchemy as sql
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
    validates,
)
from sqlalchemy.schema import FetchedValue
from sqlalchemy_utc.sqltypes import UtcDateTime

from models.orm_base import OrmBase

VALID_TYPES = [
    'easy_linear',
    'baranyi_roberts',
]

VALID_STATES = [
    'pending',
    'ready',
    'error',
]

MODEL_NAMES = {
    'easy_linear':     'Easy linear model',
    'baranyi_roberts': 'Baranyi-Roberts model',
}


class Calculation(OrmBase):
    __tablename__ = "Calculations"

    id:          Mapped[int] = mapped_column(primary_key=True)
    type:        Mapped[str] = mapped_column(sql.String(100), nullable=False)
    subjectId:   Mapped[str] = mapped_column(sql.String(100), nullable=False)
    subjectType: Mapped[str] = mapped_column(sql.String(100), nullable=False)

    measurementTechniqueId: Mapped[int] = mapped_column(
        sql.ForeignKey('MeasurementTechniques.id'),
        nullable=False,
    )
    measurementTechnique: Mapped['MeasurementTechnique'] = relationship(
        back_populates="calculations",
    )

    calculationTechniqueId: Mapped[int] = mapped_column(
        sql.ForeignKey('CalculationTechniques.id'),
        nullable=False,
    )
    calculationTechnique: Mapped['CalculationTechnique'] = relationship(
        back_populates="calculations",
    )

    bioreplicateUniqueId: Mapped[int] = mapped_column(sql.ForeignKey('Bioreplicates.id'), nullable=False)
    bioreplicate: Mapped['Bioreplicate'] = relationship(back_populates='calculations')

    coefficients: Mapped[sql.JSON] = mapped_column(sql.JSON, nullable=False)

    state: Mapped[str] = mapped_column(sql.String(100), default='pending')
    error: Mapped[str] = mapped_column(sql.String(100))

    createdAt:    Mapped[datetime] = mapped_column(UtcDateTime, server_default=FetchedValue())
    updatedAt:    Mapped[datetime] = mapped_column(UtcDateTime, server_default=FetchedValue())
    calculatedAt: Mapped[datetime] = mapped_column(UtcDateTime)

    @validates('type')
    def _validate_type(self, key, value):
        return self._validate_inclusion(key, value, VALID_TYPES)

    @validates('state')
    def _validate_state(self, key, value):
        return self._validate_inclusion(key, value, VALID_STATES)

    def get_subject(self, db_session):
        from models import Metabolite, Strain, Bioreplicate

        if self.subjectType == 'metabolite':
            return db_session.scalars(
                sql.select(Metabolite)
                .where(Metabolite.chebiId == subjectId)
                .limit(1)
            ).one_or_none()
        elif self.subjectType == 'strain':
            return db_session.get(Strain, self.subjectId)
        elif self.subjectType == 'bioreplicate':
            return db_session.get(Bioreplicate, self.subjectId)
        else:
            raise ValueError(f"Unknown subject type: {self.subjectType}")

    def generate_chart_df(self, measurements_df):
        start_time = measurements_df['time'].min()
        end_time   = measurements_df['time'].max()

        timepoints = np.linspace(start_time, end_time, 200)
        values = self._predict(timepoints)

        return pd.DataFrame.from_dict({
            'time': timepoints,
            'value': values,
            'name': MODEL_NAMES[self.type],
        })

    def _predict(self, timepoints):
        if self.type == 'easy_linear':
            return self._predict_easy_linear(timepoints)
        elif self.type == 'baranyi_roberts':
            return self._predict_baranyi_roberts(timepoints)
        else:
            raise ValueError(f"Don't know how to predict values for calculation type: {repr(self.type)}")

    def _predict_easy_linear(self, time):
        # y0    = self.coefficients['y0']
        y0_lm = self.coefficients['y0_lm']
        mumax = self.coefficients['mumax']
        # lag   = self.coefficients['lag']

        # No lag:
        # return y0 * np.exp(time * mumax)

        # Exponential:
        return y0_lm * np.exp(time * mumax)

    def _predict_baranyi_roberts(self, time):
        y0    = self.coefficients['y0']
        mumax = self.coefficients['mumax']
        K     = self.coefficients['K']
        h0    = self.coefficients['h0']

        # Formula taken from the "growthrates" documentation under `grow_baranyi`:
        # https://cran.r-project.org/web/packages/growthrates/growthrates.pdf
        #
        A = time + 1/mumax * np.log(np.exp(-mumax * time) + np.exp(-h0) - np.exp(-mumax * time - h0))
        log_y = np.log(y0) + mumax * A - np.log(1 + (np.exp(mumax * A) - 1)/np.exp(np.log(K) - np.log(y0)))

        return np.exp(log_y)
