from typing import List
import datetime

from sqlalchemy import (
    String,
    ForeignKey,
    DateTime,
    FetchedValue,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy.ext.hybrid import hybrid_property

from models.orm_base import OrmBase


class Study(OrmBase):
    __tablename__ = 'Study'

    studyUniqueID: Mapped[str] = mapped_column(String(100), primary_key=True)

    studyId:          Mapped[str] = mapped_column(String(100), nullable=False)
    studyName:        Mapped[str] = mapped_column(String(100), nullable=False)
    studyDescription: Mapped[str] = mapped_column(String,      nullable=False)
    studyURL:         Mapped[str] = mapped_column(String,      nullable=False)
    timeUnits:        Mapped[str] = mapped_column(String(100), nullable=False)

    projectUniqueID: Mapped[str] = mapped_column(ForeignKey('Project.projectUniqueID'), nullable=False)

    project: Mapped['Project'] = relationship(back_populates="studies")

    studyUsers:  Mapped[List['StudyUser']]  = relationship(back_populates="study")
    experiments: Mapped[List['Experiment']] = relationship(back_populates='study')
    strains:     Mapped[List['Strain']]     = relationship(back_populates='study')

    measurementTechniques: Mapped[List['MeasurementTechnique']] = relationship(
        back_populates="study"
    )
    studyMetabolites: Mapped[List['StudyMetabolite']] = relationship(
        back_populates="study"
    )

    createdAt:        Mapped[datetime] = mapped_column(DateTime, server_default=FetchedValue())
    updatedAt:        Mapped[datetime] = mapped_column(DateTime, server_default=FetchedValue())
    publishableAt:    Mapped[datetime] = mapped_column(DateTime)
    publishedAt:      Mapped[datetime] = mapped_column(DateTime)
    embargoExpiresAt: Mapped[datetime] = mapped_column(DateTime)

    @hybrid_property
    def isPublished(self):
        return self.publishedAt < datetime.datetime.now()
