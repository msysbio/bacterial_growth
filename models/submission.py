from datetime import datetime

from sqlalchemy import (
    String,
    ForeignKey,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy.types import JSON
from sqlalchemy.schema import FetchedValue
from sqlalchemy_utc.sqltypes import UtcDateTime

from models.orm_base import OrmBase


class Submission(OrmBase):
    __tablename__ = 'Submissions'

    id: Mapped[int] = mapped_column(primary_key=True)

    projectUniqueID: Mapped[str] = mapped_column(String(100), nullable=False)
    studyUniqueID:   Mapped[str] = mapped_column(String(100), nullable=False)
    userUniqueID:    Mapped[str] = mapped_column(String(100), nullable=False)

    project: Mapped['Project'] = relationship(
        foreign_keys=[projectUniqueID],
        primaryjoin="Submission.projectUniqueID == Project.projectUniqueID",
    )
    study: Mapped['Study'] = relationship(
        foreign_keys=[studyUniqueID],
        primaryjoin="Submission.studyUniqueID == Study.studyUniqueID",
    )

    studyDesign: Mapped[JSON] = mapped_column(JSON, nullable=False)

    studyFileId: Mapped[int] = mapped_column(ForeignKey('ExcelFiles.id'))
    dataFileId:  Mapped[int] = mapped_column(ForeignKey('ExcelFiles.id'))

    studyFile: Mapped['ExcelFile'] = relationship(
        foreign_keys=[studyFileId],
        cascade='all, delete-orphan',
        single_parent=True,
    )
    dataFile: Mapped['ExcelFile'] = relationship(
        foreign_keys=[dataFileId],
        cascade='all, delete-orphan',
        single_parent=True,
    )

    createdAt: Mapped[datetime] = mapped_column(UtcDateTime, server_default=FetchedValue())
    updatedAt: Mapped[datetime] = mapped_column(UtcDateTime, server_default=FetchedValue())

    @property
    def completed_step_count(self):
        return sum([
            1 if self.projectUniqueID and self.studyUniqueID else 0,
            1 if len(self.studyDesign.get('strains', [])) + len(self.studyDesign.get('new_strains', [])) > 0 else 0,
            1 if len(self.studyDesign.get('techniques', [])) > 0 and self.studyDesign.get('timepoint_count', 0) else 0,
            1 if self.studyFileId and self.dataFileId else 0,
            1 if self.study and self.study.isPublished else 0,
        ])

    @property
    def techniques(self):
        from models import MeasurementTechnique
        return [MeasurementTechnique(**m) for m in self.studyDesign['techniques']]
