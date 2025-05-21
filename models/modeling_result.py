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
    'logistic',
    'baranyi_roberts',
]

VALID_STATES = [
    'pending',
    'ready',
    'error',
]

MODEL_NAMES = {
    'easy_linear':     'Easy linear model',
    'logistic':        'Logistic model',
    'baranyi_roberts': 'Baranyi-Roberts model',
}


class ModelingResult(OrmBase):
    __tablename__ = "ModelingResults"

    id:   Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(sql.String(100), nullable=False)

    requestId: Mapped[int] = mapped_column(sql.ForeignKey('ModelingRequests.id'), nullable=False)
    request: Mapped['ModelingRequest'] = relationship(back_populates='results')

    measurementContextId: Mapped[int] = mapped_column(
        sql.ForeignKey('MeasurementContexts.id'),
        nullable=False,
    )
    measurementContext: Mapped['MeasurementContext'] = relationship(back_populates='modelingResults')

    inputs:       Mapped[sql.JSON] = mapped_column(sql.JSON, nullable=False)
    fit:          Mapped[sql.JSON] = mapped_column(sql.JSON, nullable=False)
    coefficients: Mapped[sql.JSON] = mapped_column(sql.JSON, nullable=False)

    state: Mapped[str] = mapped_column(sql.String(100), default='pending')
    error: Mapped[str] = mapped_column(sql.String(100))

    createdAt:    Mapped[datetime] = mapped_column(UtcDateTime, server_default=FetchedValue())
    updatedAt:    Mapped[datetime] = mapped_column(UtcDateTime, server_default=FetchedValue())
    calculatedAt: Mapped[datetime] = mapped_column(UtcDateTime)

    @classmethod
    def empty_coefficients(Self, model_type):
        if model_type == 'easy_linear':
            return {'y0': None, 'y0_lm': None, 'mumax': None, 'lag': None}
        elif model_type == 'logistic':
            return {'y0': None, 'mumax': None, 'K': None}
        elif model_type == 'baranyi_roberts':
            return {'y0': None, 'mumax': None, 'K': None, 'h0': None}
        else:
            raise ValueError(f"Don't know what the coefficients are for model type: {repr(model_type)}")

    @classmethod
    def empty_fit(Self):
        return {'r2': None, 'rss': None}

    @classmethod
    def empty_inputs(Self, model_type):
        if model_type == 'easy_linear':
            return {'pointCount': '5'}
        elif model_type in ('logistic', 'baranyi_roberts'):
            return {'endTime': ''}
        else:
            return {}

    @property
    def model_name(self):
        return MODEL_NAMES[self.type]

    @validates('type')
    def _validate_type(self, key, value):
        return self._validate_inclusion(key, value, VALID_TYPES)

    @validates('state')
    def _validate_state(self, key, value):
        return self._validate_inclusion(key, value, VALID_STATES)

    def generate_chart_df(self, measurements_df):
        start_time = measurements_df['time'].min()
        end_time   = measurements_df['time'].max()

        timepoints = np.linspace(start_time, end_time, 200)
        values = self._predict(timepoints)

        return pd.DataFrame.from_dict({
            'time': timepoints,
            'value': values,
        })

    def _predict(self, timepoints):
        if self.type == 'easy_linear':
            return self._predict_easy_linear(timepoints)
        elif self.type == 'logistic':
            return self._predict_logistic(timepoints)
        elif self.type == 'baranyi_roberts':
            return self._predict_baranyi_roberts(timepoints)
        else:
            raise ValueError(f"Don't know how to predict values for model type: {repr(self.type)}")

    def _predict_easy_linear(self, time):
        y0    = float(self.coefficients['y0'])
        y0_lm = float(self.coefficients['y0_lm'])
        mumax = float(self.coefficients['mumax'])
        # lag   = float(self.coefficients['lag'])

        # No lag:
        # return y0 * np.exp(time * mumax)

        # Exponential:
        return y0_lm * np.exp(time * mumax)

    def _predict_logistic(self, time):
        y0    = float(self.coefficients['y0'])
        mumax = float(self.coefficients['mumax'])
        K     = float(self.coefficients['K'])

        return (K * y0)/(y0 + (K - y0) * np.exp(-mumax * time))

    def _predict_baranyi_roberts(self, time):
        y0    = float(self.coefficients['y0'])
        mumax = float(self.coefficients['mumax'])
        K     = float(self.coefficients['K'])
        h0    = float(self.coefficients['h0'])

        # Formula taken from the "growthrates" documentation under `grow_baranyi`:
        # https://cran.r-project.org/web/packages/growthrates/growthrates.pdf
        #
        A = time + 1/mumax * np.log(np.exp(-mumax * time) + np.exp(-h0) - np.exp(-mumax * time - h0))
        log_y = np.log(y0) + mumax * A - np.log(1 + (np.exp(mumax * A) - 1)/np.exp(np.log(K) - np.log(y0)))

        return np.exp(log_y)
