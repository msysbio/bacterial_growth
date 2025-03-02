from sqlalchemy import String
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from lib.db import execute_text
from models.orm_base import OrmBase


class Strain(OrmBase):
    __tablename__ = 'Strains'

    strainId: Mapped[int] = mapped_column(primary_key=True)
    memberName: Mapped[str] = mapped_column(String)

    @staticmethod
    def find_for_study(db_conn, study_id, strain_name):
        return execute_text(db_conn, """
            SELECT strainId
            FROM Strains
            WHERE studyId = :study_id
              AND memberName = :strain_name
        """, study_id=study_id, strain_name=strain_name).scalar()
