from sqlalchemy import ForeignKey
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from models.orm_base import OrmBase


class StudyMetabolite(OrmBase):
    __tablename__ = 'MetabolitePerExperiment'

    studyId:            Mapped[str] = mapped_column(ForeignKey("Study"),       primary_key=True)
    chebi_id:           Mapped[str] = mapped_column(ForeignKey('Metabolites'), primary_key=True)
    experimentUniqueId: Mapped[int] = mapped_column(ForeignKey('Experiments'), primary_key=True)

    bioreplicateUniqueId: Mapped[int] = mapped_column(
        ForeignKey('BioReplicatesPerExperiment'),
        nullable=False,
    )

    study:      Mapped['Study']      = relationship(back_populates="studyMetabolites")
    metabolite: Mapped['Metabolite'] = relationship(back_populates="studyMetabolites")
