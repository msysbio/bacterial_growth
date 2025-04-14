from typing import List

from sqlalchemy import (
    String,
    Integer,
    ForeignKey,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from models.orm_base import OrmBase


class ProjectUser(OrmBase):
    __tablename__ = 'ProjectUsers'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    projectUniqueID: Mapped[str] = mapped_column(ForeignKey('Project.projectUniqueID'), nullable=False)
    userUniqueID:    Mapped[str] = mapped_column(String(100), nullable=False)

    project: Mapped[List['Project']] = relationship(back_populates="projectUsers")
