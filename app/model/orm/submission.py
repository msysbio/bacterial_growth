from typing import Optional
from datetime import datetime

import sqlalchemy as sql
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy.types import JSON
from sqlalchemy.schema import FetchedValue
from sqlalchemy_utc.sqltypes import UtcDateTime

from app.model.orm.orm_base import OrmBase


class Submission(OrmBase):
    __tablename__ = 'Submissions'

    id: Mapped[int] = mapped_column(primary_key=True)

    projectUniqueID: Mapped[str] = mapped_column(sql.String(100), nullable=False)
    studyUniqueID:   Mapped[str] = mapped_column(sql.String(100), nullable=False)

    project: Mapped[Optional['Project']] = relationship(
        foreign_keys=[projectUniqueID],
        primaryjoin="Submission.projectUniqueID == Project.projectUniqueID",
    )
    study: Mapped[Optional['Study']] = relationship(
        foreign_keys=[studyUniqueID],
        primaryjoin="Submission.studyUniqueID == Study.studyUniqueID",
    )

    userUniqueID: Mapped[str] = mapped_column(sql.ForeignKey('Users.uuid'), nullable=False)
    user: Mapped['User'] = relationship(back_populates='submissions')

    studyDesign: Mapped[JSON] = mapped_column(JSON, nullable=False)

    dataFileId: Mapped[int] = mapped_column(sql.ForeignKey('ExcelFiles.id'), nullable=True)
    dataFile: Mapped[Optional['ExcelFile']] = relationship(
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
            1 if len(self.studyDesign.get('strains', [])) + len(self.studyDesign.get('custom_strains', [])) > 0 else 0,
            1 if len(self.studyDesign.get('techniques', [])) > 0 else 0,
            1 if len(self.studyDesign.get('compartments', [])) > 0 and len(self.studyDesign.get('communities', [])) > 0 else 0,
            1 if len(self.studyDesign.get('experiments', [])) > 0 else 0,
            1 if self.dataFileId else 0,
            1 if self.study and self.study.isPublished else 0,
        ])

    def build_techniques(self):
        from app.model.orm import MeasurementTechnique
        return [MeasurementTechnique(**m) for m in self.studyDesign['techniques']]
