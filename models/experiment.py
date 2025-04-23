from typing import List

import sqlalchemy as sql
from sqlalchemy import (
    String,
    ForeignKey,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy.ext.hybrid import hybrid_property

from models.orm_base import OrmBase


class Experiment(OrmBase):
    __tablename__ = "Experiments"

    experimentUniqueId: Mapped[int] = mapped_column(primary_key=True)

    experimentId:          Mapped[str] = mapped_column(String(100), nullable=False)
    experimentDescription: Mapped[str] = mapped_column(String)

    bioreplicates: Mapped[List['Bioreplicate']] = relationship(
        order_by="Bioreplicate.bioreplicateUniqueId",
        back_populates='experiment',
        cascade="all, delete-orphan"
    )

    studyId: Mapped[str] = mapped_column(ForeignKey('Study'), nullable=False)
    study: Mapped['Study'] = relationship(back_populates='experiments')

    cultivationMode:    Mapped[str] = mapped_column(String(50))
    controlDescription: Mapped[str] = mapped_column(String)

    @hybrid_property
    def id(self):
        return self.experimentUniqueId

    @hybrid_property
    def name(self):
        return self.experimentId

    @hybrid_property
    def description(self):
        return self.experimentDescription

    @property
    def measurements(self):
        for bioreplicate in self.bioreplicates:
            for measurement in bioreplicate.measurements:
                yield measurement


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
