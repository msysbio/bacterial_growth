import sqlalchemy as sql
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.model.orm.orm_base import OrmBase


class ProjectUser(OrmBase):
    __tablename__ = 'ProjectUsers'

    id: Mapped[int] = mapped_column(sql.Integer, primary_key=True)

    projectUniqueID: Mapped[str] = mapped_column(sql.ForeignKey('Projects.projectUniqueID'), nullable=False)
    userUniqueID:    Mapped[str] = mapped_column(sql.ForeignKey('Users.uuid'),               nullable=False)

    project: Mapped['Project'] = relationship(back_populates="projectUsers")
    user:    Mapped['User']    = relationship(back_populates="projectUsers")
