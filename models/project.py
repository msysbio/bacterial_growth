from typing import List

import sqlalchemy as sql
from sqlalchemy import String
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy.ext.hybrid import hybrid_property

from models.orm_base import OrmBase


class Project(OrmBase):
    __tablename__ = 'Project'

    projectUniqueID: Mapped[str] = mapped_column(String(100), primary_key=True)

    projectId:          Mapped[str] = mapped_column(String(100), nullable=False)
    projectName:        Mapped[str] = mapped_column(String(100), nullable=False)
    projectDescription: Mapped[str] = mapped_column(String,      nullable=False)

    projectUsers: Mapped[List['ProjectUser']] = relationship(back_populates="project")
    studies:      Mapped[List['Study']]       = relationship(back_populates="project")

    @hybrid_property
    def publicId(self):
        return self.projectId

    @hybrid_property
    def uuid(self):
        return self.projectUniqueID

    @hybrid_property
    def name(self):
        return self.projectName

    @property
    def studyUuids(self):
        return [s.studyUniqueID for s in self.studies]

    @property
    def linkedUserUuids(self):
        return {pu.userUniqueID for pu in self.projectUsers}

    @staticmethod
    def find_available_id(db_conn):
        query           = "SELECT IFNULL(COUNT(*), 0) FROM Project;"
        number_projects = db_conn.execute(sql.text(query)).scalar()
        next_number     = int(number_projects) + 1
        next_id         = "PMGDB{:06d}".format(next_number)

        return next_id
