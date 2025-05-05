import sqlalchemy as sql
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from models.orm_base import OrmBase


class StudyMetabolite(OrmBase):
    __tablename__ = 'MetabolitePerExperiment'

    studyId:            Mapped[str] = mapped_column(sql.ForeignKey("Study"),          primary_key=True)
    chebi_id:           Mapped[str] = mapped_column(sql.ForeignKey('Metabolites'),    primary_key=True)
    experimentUniqueId: Mapped[int] = mapped_column(sql.ForeignKey('Experiments.id'), primary_key=True)

    bioreplicateUniqueId: Mapped[int] = mapped_column(sql.ForeignKey('Bioreplicates.id'), nullable=False)

    study:      Mapped['Study']      = relationship(back_populates="studyMetabolites")
    metabolite: Mapped['Metabolite'] = relationship(back_populates="studyMetabolites")
