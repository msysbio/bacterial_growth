import sqlalchemy as sql
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from models.orm_base import OrmBase


class StudyMetabolite(OrmBase):
    __tablename__ = 'StudyMetabolites'

    id: Mapped[int] = mapped_column(sql.Integer, primary_key=True, autoincrement=True)

    studyId:  Mapped[str] = mapped_column(sql.ForeignKey('Study.studyId'),       primary_key=True)
    chebi_id: Mapped[str] = mapped_column(sql.ForeignKey('Metabolites.chebiId'), primary_key=True)

    study:      Mapped['Study']      = relationship(back_populates="studyMetabolites")
    metabolite: Mapped['Metabolite'] = relationship(back_populates="studyMetabolites")
