import sqlalchemy as sql
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from lib.db import execute_text
from models.orm_base import OrmBase


class Strain(OrmBase):
    __tablename__ = 'Strains'

    id: Mapped[int] = mapped_column(sql.Integer, primary_key=True)

    name:        Mapped[str]  = mapped_column(sql.String(100))
    description: Mapped[str]  = mapped_column(sql.String)

    defined: Mapped[bool] = mapped_column(sql.Boolean, nullable=False, default=True)
    NCBId:   Mapped[int]  = mapped_column(sql.Integer)

    studyId: Mapped[str] = mapped_column(sql.ForeignKey('Study.studyId'), nullable=False)
    study: Mapped['Study'] = relationship(back_populates="strains")

    userUniqueID: Mapped[str] = mapped_column(sql.String(100))

    def __lt__(self, other):
        return self.name < other.name

    @staticmethod
    def find_for_study(db_conn, study_id, strain_name):
        return execute_text(db_conn, """
            SELECT strainId
            FROM Strains
            WHERE studyId = :study_id
              AND name = :strain_name
        """, study_id=study_id, strain_name=strain_name).scalar()
