import sqlalchemy as sql

class Taxon():
    @staticmethod
    def search_by_name(db_conn, term, page=1, per_page=10):
        term = term.lower()

        query = """
            SELECT
                tax_id AS id,
                tax_names AS text
            FROM Taxa
            WHERE LOWER(tax_names) LIKE :term_pattern
            ORDER BY
                LOCATE(:term, LOWER(tax_names)) ASC,
                tax_names ASC
            LIMIT :per_page
            OFFSET :offset
        """
        results = db_conn.execute(sql.text(query), {
            'term': term,
            'term_pattern': f'%{term}%',
            'per_page': per_page,
            'offset': (page - 1) * per_page,
        }).all()
        results = [row._asdict() for row in results]

        count_query = """
            SELECT COUNT(*)
            FROM Taxa
            WHERE LOWER(tax_names) LIKE LOWER(:term)
        """
        total_count = db_conn.execute(sql.text(count_query), {'term': f'%{term}%'}).scalar()
        has_more = (page * per_page < total_count)

        return results, has_more
