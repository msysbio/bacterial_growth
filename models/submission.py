from datetime import datetime

import sqlalchemy as sql
from sqlalchemy import (
    String,
    LargeBinary,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)
from sqlalchemy.types import (
    JSON,
    DateTime,
)
from sqlalchemy.schema import FetchedValue

from models.orm_base import OrmBase


class Submission(OrmBase):
    __tablename__ = 'Submissions'

    id: Mapped[int] = mapped_column(primary_key=True)

    projectUniqueID: Mapped[str] = mapped_column(String(100), nullable=False)
    studyUniqueID:   Mapped[str] = mapped_column(String(100), nullable=False)
    userUniqueID:    Mapped[str] = mapped_column(String(100), nullable=False)

    studyDesign: Mapped[JSON] = mapped_column(JSON, nullable=False)

    studyXls: Mapped[bytes | None] = mapped_column(LargeBinary)
    dataXls:  Mapped[bytes | None] = mapped_column(LargeBinary)

    createdAt: Mapped[datetime] = mapped_column(DateTime, server_default=FetchedValue())
    updatedAt: Mapped[datetime] = mapped_column(DateTime, server_default=FetchedValue())

    @property
    def completed_step_count(self):
        return sum([
            1 if self.projectUniqueID and self.studyUniqueID else 0,
            1 if len(self.studyDesign['strains']) + len(self.studyDesign['new_strains']) > 0 else 0,
            1 if len(self.studyDesign['technique_types']) > 0 and self.studyDesign['timepoint_count'] else 0,
            1 if self.studyXls and self.dataXls else 0,
            0, # final step
        ])
