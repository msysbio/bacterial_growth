from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.inspection import inspect
from sqlalchemy import LargeBinary


class OrmBase(DeclarativeBase):
    @classmethod
    def filter_keys(Self, data: dict):
        return {k: v for k, v in data.items() if hasattr(Self, k)}

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def _asdict(self):
        return {
            c.name: "<BLOB>" if isinstance(c.type, LargeBinary) else getattr(self, c.name)
            for c in inspect(type(self)).c
        }

    def __str__(self):
        parts = []

        if hasattr(self, 'id'):
            parts.append(f"id={self.id}")
        if hasattr(self, 'publicId'):
            parts.append(f"publicId={self.publicId}")

        return f"<{type(self).__name__} {', '.join(parts)}>"

    def __repr__(self):
        return f"{type(self).__name__}({', '.join([f"{k}={repr(v)}" for k, v in self._asdict().items()])}>"

    def _validate_inclusion(self, key, value, valid_values):
        if value not in valid_values:
            raise ValueError(f"Invalid value for {key}: {repr(value)}, must be one of {repr(valid_values)}")
        return value
