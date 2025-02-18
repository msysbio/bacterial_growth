from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.inspection import inspect

class OrmBase(DeclarativeBase):
    def _asdict(self):
        return { c.name: getattr(self, c.name) for c in inspect(type(self)).c }

    def __str__(self):
        return f"<{type(self).__name__} {self._asdict()}>"
