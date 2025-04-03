from typing import List

from sqlalchemy import String
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from models.orm_base import OrmBase


class Project(OrmBase):
    __tablename__ = 'Project'

    projectUniqueID: Mapped[str] = mapped_column(String(100), primary_key=True)

    projectId:   Mapped[str] = mapped_column(String(100), nullable=False)
    projectName: Mapped[str] = mapped_column(String(100), nullable=False)
