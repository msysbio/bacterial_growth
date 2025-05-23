from datetime import datetime
from io import BytesIO

import sqlalchemy as sql
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)
from sqlalchemy.schema import FetchedValue
from sqlalchemy_utc.sqltypes import UtcDateTime
import humanize
import pandas as pd

from app.model.orm.orm_base import OrmBase


class ExcelFile(OrmBase):
    __tablename__ = 'ExcelFiles'

    id: Mapped[int] = mapped_column(primary_key=True)

    filename: Mapped[str]   = mapped_column(sql.String(255))
    size:     Mapped[int]   = mapped_column(sql.Integer)
    content:  Mapped[bytes] = mapped_column(sql.LargeBinary)

    createdAt: Mapped[datetime] = mapped_column(UtcDateTime, server_default=FetchedValue())

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

    def extract_sheets(self):
        excel = pd.ExcelFile(BytesIO(self.content))

        sheets = {
            name: pd.read_excel(excel, sheet_name=name)
            for name in excel.sheet_names
        }

        return sheets
