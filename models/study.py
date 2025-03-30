from typing import List

from sqlalchemy import (
    String,
    ForeignKey,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from models.orm_base import OrmBase


class Study(OrmBase):
    __tablename__ = 'Study'

    studyUniqueID: Mapped[str] = mapped_column(String(100), primary_key=True)

    studyId:          Mapped[str] = mapped_column(String(100), nullable=False)
    studyName:        Mapped[str] = mapped_column(String(100), nullable=False)
    studyDescription: Mapped[str] = mapped_column(String,      nullable=False)

    projectUniqueID: Mapped[str] = mapped_column(ForeignKey('Project.projectUniqueID'), nullable=False)

    studyUsers: Mapped[List['StudyUser']] = relationship(
        back_populates="study"
    )

    project: Mapped['Project'] = relationship(back_populates="studies")

    experiments: Mapped[List['Experiment']] = relationship(
        back_populates='study',
        cascade="all, delete-orphan"
    )

    measurementTechniques: Mapped[List['MeasurementTechnique']] = relationship(
        back_populates="study"
    )
