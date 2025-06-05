from datetime import datetime

import sqlalchemy as sql
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)
from sqlalchemy_utc.sqltypes import UtcDateTime

from app.model.orm.orm_base import OrmBase
from app.model.lib import orcid


class User(OrmBase):
    __tablename__ = 'Users'

    id: Mapped[int] = mapped_column(primary_key=True)

    uuid:       Mapped[str] = mapped_column(sql.String(100), nullable=False)
    orcidId:    Mapped[str] = mapped_column(sql.String(100), nullable=False)
    orcidToken: Mapped[str] = mapped_column(sql.String(100), nullable=False)

    name:    Mapped[str]  = mapped_column(sql.String(255), nullable=False)
    isAdmin: Mapped[bool] = mapped_column(sql.Boolean, nullable=False, default=False)

    createdAt:   Mapped[datetime] = mapped_column(UtcDateTime, server_default=sql.FetchedValue())
    updatedAt:   Mapped[datetime] = mapped_column(UtcDateTime, server_default=sql.FetchedValue())
    lastLoginAt: Mapped[datetime] = mapped_column(UtcDateTime, nullable=True)

    @property
    def orcidUrl(self):
        return orcid.get_user_url(self)
