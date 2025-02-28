from typing import List

from sqlalchemy import (
    Enum,
    Integer,
    String,
    Numeric,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from models.orm_base import OrmBase
from lib.db import execute_text


class Bioreplicate(OrmBase):
    __tablename__ = 'BioReplicatesPerExperiment'

    bioreplicateUniqueId: Mapped[int] = mapped_column(primary_key=True)
    bioreplicateId:       Mapped[str] = mapped_column(String(100), nullable=False)

    studyId:      Mapped[str] = mapped_column(String(100), nullable=False)
    experimentId: Mapped[str] = mapped_column(String(100), nullable=False)

    measurements: Mapped[List["Measurement"]] = relationship(
        back_populates="bioreplicate", cascade="all, delete-orphan"
    )

    @staticmethod
    def find_for_study(db_conn, study_id, bioreplicate_id):
        return execute_text(db_conn, """
            SELECT bioreplicateUniqueId
            FROM BioReplicatesPerExperiment
            WHERE studyId = :study_id
              AND bioreplicateId = :bioreplicate_id
        """, study_id=study_id, bioreplicate_id=bioreplicate_id).scalar()
