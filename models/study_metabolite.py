import sqlalchemy as sql
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from models.orm_base import OrmBase


class StudyMetabolite(OrmBase):
    __tablename__ = 'StudyMetabolites'

    id: Mapped[int] = mapped_column(primary_key=True)

    studyId:  Mapped[str] = mapped_column(sql.ForeignKey('Study.studyId'),        primary_key=True)
    chebi_id: Mapped[str] = mapped_column(sql.ForeignKey('Metabolites.chebi_id'), primary_key=True)

    study:      Mapped['Study']      = relationship(back_populates="studyMetabolites")
    metabolite: Mapped['Metabolite'] = relationship(back_populates="studyMetabolites")
