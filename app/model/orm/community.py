from typing import List

import sqlalchemy as sql
from sqlalchemy.orm import (
    mapped_column,
    relationship,
    Mapped,
)
from sqlalchemy.types import JSON

from app.model.orm.orm_base import OrmBase


class Community(OrmBase):
    __tablename__ = "Communities"

    id:   Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(sql.String(100), nullable=False)

    # Note: convert to studyUniqueID or delete
    studyId: Mapped[str] = mapped_column(sql.ForeignKey('Study.studyId'), nullable=False)
    study: Mapped['Study'] = relationship(back_populates='communities')

    strainIds: Mapped[JSON] = mapped_column(JSON, nullable=False)

    experiments: Mapped[List['Experiment']] = relationship(back_populates='community')

    # TODO make a join table to strains, this is silly
    def get_strains(self, db_session):
        from app.model.orm import Strain

        return db_session.scalars(
            sql.select(Strain)
            .where(Strain.id.in_(self.strainIds))
        ).all()
