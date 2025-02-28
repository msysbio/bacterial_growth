import sqlalchemy as sql
from sqlalchemy import (
    Enum,
    Integer,
    String,
    Numeric,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from models.orm_base import OrmBase

# TODO (2024-09-26) Duplicates taxa completion a lot, try to make completion
# logic generic, to an extent.
#
class Metabolite(OrmBase):
    __tablename__ = 'Metabolites'

    chebi_id:    Mapped[str] = mapped_column(primary_key=True)
    metabo_name: Mapped[str] = mapped_column(String(100), nullable=False)

    @staticmethod
    def search_by_name(db_conn, term, page=1, per_page=10):
        term = term.lower().strip()
        if len(term) <= 0:
            return [], 0

        term_pattern = '%' + '%'.join(term.split()) + '%'
        first_word = term.split()[0]

        query = """
            SELECT
                chebi_id AS id,
                metabo_name AS text
            FROM Metabolites
            WHERE LOWER(metabo_name) LIKE :term_pattern
            ORDER BY
                LOCATE(:first_word, LOWER(metabo_name)) ASC,
                metabo_name ASC
            LIMIT :per_page
            OFFSET :offset
        """
        results = db_conn.execute(sql.text(query), {
            'first_word': term,
            'term_pattern': term_pattern,
            'per_page': per_page,
            'offset': (page - 1) * per_page,
        }).all()
        results = [row._asdict() for row in results]

        count_query = """
            SELECT COUNT(*)
            FROM Metabolites
            WHERE LOWER(metabo_name) LIKE :term_pattern
        """
        total_count = db_conn.execute(sql.text(count_query), {'term_pattern': term_pattern}).scalar()
        has_more = (page * per_page < total_count)

        return results, has_more
