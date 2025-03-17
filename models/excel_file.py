from datetime import datetime

from sqlalchemy import (
    String,
    LargeBinary,
    Integer,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)
from sqlalchemy.types import DateTime
from sqlalchemy.schema import FetchedValue
import humanize

from models.orm_base import OrmBase


class ExcelFile(OrmBase):
    __tablename__ = 'ExcelFiles'

    id: Mapped[int] = mapped_column(primary_key=True)

    filename: Mapped[str]   = mapped_column(String(255))
    size:     Mapped[int]   = mapped_column(Integer)
    content:  Mapped[bytes] = mapped_column(LargeBinary)

    createdAt: Mapped[datetime] = mapped_column(DateTime, server_default=FetchedValue())

    @classmethod
    def from_upload(Self, uploaded_file):
        file = ExcelFile()

        file.filename = uploaded_file.filename
        file.content  = uploaded_file.read()
        file.size     = len(file.content)

        return file

    @property
    def humanized_size(self):
        return humanize.naturalsize(self.size)
