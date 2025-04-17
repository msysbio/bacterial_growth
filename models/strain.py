from sqlalchemy import (
    String,
    ForeignKey,
    Boolean,
    Integer,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy.ext.hybrid import hybrid_property

from lib.db import execute_text
from models.orm_base import OrmBase


class Strain(OrmBase):
    __tablename__ = 'Strains'

    strainId: Mapped[int] = mapped_column(primary_key=True)

    memberId:          Mapped[str]  = mapped_column(String(50))
    memberName:        Mapped[str]  = mapped_column(String)
    descriptionMember: Mapped[str]  = mapped_column(String)

    defined: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    NCBId:   Mapped[int]  = mapped_column(Integer)

    studyId: Mapped[str] = mapped_column(ForeignKey('Study'), nullable=False)
    study: Mapped['Study'] = relationship(back_populates="strains")

    userUniqueID: Mapped[str] = mapped_column(String(100))

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
