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


class StudyMetabolite(OrmBase):
    __tablename__ = 'MetabolitePerExperiment'

    studyId: Mapped[str] = mapped_column(
        ForeignKey("Study.studyId"),
        nullable=False,
        primary_key=True,
    )
    chebi_id: Mapped[str] = mapped_column(
        ForeignKey('Metabolites.chebi_id'),
        primary_key=True,
    )
    experimentUniqueId: Mapped[int] = mapped_column(
        ForeignKey('Experiments'),
        nullable=False,
        primary_key=True,
    )

    study:      Mapped['Study']      = relationship(back_populates="studyMetabolites")
    metabolite: Mapped['Metabolite'] = relationship(back_populates="studyMetabolites")
