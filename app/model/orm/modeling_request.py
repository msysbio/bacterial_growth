from datetime import datetime
from typing import List

import sqlalchemy as sql
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
    validates,
)
from sqlalchemy.schema import FetchedValue
from sqlalchemy_utc.sqltypes import UtcDateTime

from app.model.orm.orm_base import OrmBase

VALID_TYPES = [
    'easy_linear',
    'logistic',
    'baranyi_roberts',
]

VALID_STATES = [
    'pending',
    'in_progress',
    'ready',
    'error',
]

MODEL_NAMES = {
    'easy_linear':     '"Easy linear" method',
    'logistic':        'Logistic model',
    'baranyi_roberts': 'Baranyi-Roberts model',
}


class ModelingRequest(OrmBase):
    __tablename__ = "ModelingRequests"

    id:   Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(sql.String(100), nullable=False)

    studyId: Mapped[str] = mapped_column(sql.ForeignKey('Studies.studyId'), nullable=False)
    study: Mapped['Study'] = relationship(back_populates='modelingRequests')

    jobUuid: Mapped[str] = mapped_column(sql.String(100))
    state:   Mapped[str] = mapped_column(sql.String(100), default='pending')
    error:   Mapped[str] = mapped_column(sql.String)

    createdAt: Mapped[datetime] = mapped_column(UtcDateTime, server_default=FetchedValue())
    updatedAt: Mapped[datetime] = mapped_column(UtcDateTime, server_default=FetchedValue())

    results: Mapped[List['ModelingResult']] = relationship(
        back_populates='request',
        cascade='all, delete-orphan'
    )

    @validates('type')
    def _validate_type(self, key, value):
        return self._validate_inclusion(key, value, VALID_TYPES)

    @validates('state')
    def _validate_state(self, key, value):
        return self._validate_inclusion(key, value, VALID_STATES)

    @property
    def long_name(self):
        return MODEL_NAMES[self.type]
