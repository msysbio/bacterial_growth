import io

from flask import (
    g,
    send_file,
)
import sqlalchemy as sql
from werkzeug.exceptions import Forbidden, NotFound

from app.model.orm import (
    ExcelFile,
    Submission,
)


def download_excel_file(id):
    file = g.db_session.get(ExcelFile, id)
    if not file:
        raise NotFound()

    if not g.current_user:
        raise Forbidden()

    submission_user_ids = g.db_session.scalars(
        sql.select(Submission.userUniqueID)
        .distinct()
        .where(Submission.dataFileId == file.id)
    ).all()

    allowed_user_ids = set(submission_user_ids)

    # TODO (2025-04-14) Add a check for already-submitted studies, once we plug in studyId

    if g.current_user.uuid not in allowed_user_ids:
        raise Forbidden()

    return send_file(
        io.BytesIO(file.content),
        as_attachment=True,
        download_name=file.filename
    )
