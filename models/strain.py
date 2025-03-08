from sqlalchemy import String
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)
from sqlalchemy.ext.hybrid import hybrid_property

from lib.db import execute_text
from models.orm_base import OrmBase


class Strain(OrmBase):
    __tablename__ = 'Strains'

    strainId: Mapped[int] = mapped_column(primary_key=True)
    memberName: Mapped[str] = mapped_column(String)

    def __lt__(self, other):
        return self.memberName < other.memberName

    @hybrid_property
    def id(self):
        return self.strainId

    @hybrid_property
    def name(self):
        return self.memberName

    @staticmethod
    def find_for_study(db_conn, study_id, strain_name):
        return execute_text(db_conn, """
            SELECT strainId
            FROM Strains
            WHERE studyId = :study_id
              AND memberName = :strain_name
        """, study_id=study_id, strain_name=strain_name).scalar()
