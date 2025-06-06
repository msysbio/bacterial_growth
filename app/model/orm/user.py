from datetime import datetime
from typing import List

import sqlalchemy as sql
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy_utc.sqltypes import UtcDateTime

from app.model.orm.orm_base import OrmBase
from app.model.lib import orcid


class User(OrmBase):
    __tablename__ = 'Users'

    # A relationship representing ownership of these records. Clearing them out
    # should directly delete them so they can be replaced.
    owner_relationship = lambda: relationship(
        back_populates='user',
        cascade='all, delete-orphan',
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    uuid:       Mapped[str] = mapped_column(sql.String(100), nullable=False)
    orcidId:    Mapped[str] = mapped_column(sql.String(100), nullable=False)
    orcidToken: Mapped[str] = mapped_column(sql.String(100), nullable=False)

    name:    Mapped[str]  = mapped_column(sql.String(255), nullable=False)
    isAdmin: Mapped[bool] = mapped_column(sql.Boolean, nullable=False, default=False)

    createdAt:   Mapped[datetime] = mapped_column(UtcDateTime, server_default=sql.FetchedValue())
    updatedAt:   Mapped[datetime] = mapped_column(UtcDateTime, server_default=sql.FetchedValue())
    lastLoginAt: Mapped[datetime] = mapped_column(UtcDateTime, nullable=True)

    ownedProjects: Mapped[List['Project']] = relationship(back_populates='owner')
    ownedStudies:  Mapped[List['Study']]   = relationship(back_populates='owner')

    submissions: Mapped[List['Submission']] = relationship(
        back_populates='user',
    )

    studyUsers: Mapped[List['StudyUser']] = owner_relationship()
    managedStudies: Mapped[List['Study']] = relationship(
        secondary='StudyUsers',
        viewonly=True,
    )

    projectUsers: Mapped[List['ProjectUser']] = owner_relationship()
    managedProjects: Mapped[List['Project']] = relationship(
        secondary='ProjectUsers',
        viewonly=True,
    )

    @property
    def orcidUrl(self):
        return orcid.get_user_url(self)
