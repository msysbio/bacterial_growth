from typing import List

import sqlalchemy as sql
from sqlalchemy import String
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from models.orm_base import OrmBase
from models.bioreplicate import Bioreplicate


class Experiment(OrmBase):
    __tablename__ = "Experiments"

    experimentUniqueId: Mapped[int] = mapped_column(primary_key=True)

    experimentId:          Mapped[str] = mapped_column(String(100), nullable=False)
    experimentDescription: Mapped[str] = mapped_column(String)

    bioreplicates: Mapped[List['Bioreplicate']] = relationship(
        back_populates='experiment',
        cascade="all, delete-orphan"
    )

    studyId: Mapped[str] = mapped_column(String(100), nullable=False)


def get_experiment(experimentUniqueId, conn):
    query = """
        SELECT
            E.experimentId,
            E.experimentUniqueId,
            E.experimentDescription,
            GROUP_CONCAT(DISTINCT BRI.bioreplicateId) AS bioreplicateIds
        FROM
            Experiments AS E
        LEFT JOIN
            BioReplicatesPerExperiment AS BRI ON E.experimentUniqueId = BRI.experimentUniqueId
        WHERE
            E.experimentUniqueId = :experimentUniqueId
        GROUP BY
            E.experimentId,
            E.experimentDescription
    """
    return conn.execute(sql.text(query), {'experimentUniqueId': experimentUniqueId}).one()._asdict()
