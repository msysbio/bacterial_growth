from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.inspection import inspect
from sqlalchemy import LargeBinary


class OrmBase(DeclarativeBase):
    def _asdict(self):
        return {
            c.name: "<BLOB>" if isinstance(c.type, LargeBinary) else getattr(self, c.name)
            for c in inspect(type(self)).c
        }

    def __str__(self):
        return f"<{type(self).__name__} {self._asdict()}>"

    def _validate_inclusion(self, key, value, valid_values):
        if value not in valid_values:
            raise ValueError(f"Invalid value for {key}: {repr(value)}, must be one of {repr(valid_values)}")
        return value

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
