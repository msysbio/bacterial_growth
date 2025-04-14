import re

import sqlalchemy as sql
from sqlalchemy import String
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from models.orm_base import OrmBase

class Taxon(OrmBase):
    __tablename__ = 'Taxa'

    tax_id:    Mapped[str] = mapped_column(String(512), primary_key=True)
    tax_names: Mapped[str] = mapped_column(String(512))

    @property
    def short_name(self):
        return re.sub(r'^([A-Z])[A-Za-z]+ ', r'\1. ', self.tax_names)

    @staticmethod
    def search_by_name(db_conn, term, page=1, per_page=10):
        term = term.lower().strip()
        if len(term) <= 0:
            return [], 0

        term_pattern = '%' + '%'.join(term.split()) + '%'
        first_word = term.split()[0]

        query = """
            SELECT
                tax_id AS id,
                CONCAT(tax_names, ' (NCBI:', tax_id, ')') AS text
            FROM Taxa
            WHERE LOWER(tax_names) LIKE :term_pattern
            ORDER BY
                LOCATE(:first_word, LOWER(tax_names)) ASC,
                tax_names ASC
            LIMIT :per_page
            OFFSET :offset
        """
        results = db_conn.execute(sql.text(query), {
            'first_word': first_word,
            'term_pattern': term_pattern,
            'per_page': per_page,
            'offset': (page - 1) * per_page,
        }).all()
        results = [row._asdict() for row in results]

        count_query = """
            SELECT COUNT(*)
            FROM Taxa
            WHERE LOWER(tax_names) LIKE :term_pattern
        """
        total_count = db_conn.execute(sql.text(count_query), {'term_pattern': term_pattern}).scalar()
        has_more = (page * per_page < total_count)

        return results, has_more
