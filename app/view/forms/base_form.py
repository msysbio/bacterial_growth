from flask_wtf import FlaskForm
from wtforms.validators import ValidationError

from app.model.lib.util import humanize_camelcased_string


class BaseForm(FlaskForm):
    def get_template(self, subclass_name):
        return getattr(self.__class__, subclass_name)()

    @property
    def error_messages(self):
        return list(_iterate_error_messages(prefixes=[], errors=self.errors))

    def _validate_uniqueness(self, message, value_list):
        seen       = set()
        duplicated = set()

        for value in value_list:
            if value in seen:
                duplicated.add(value)
            else:
                seen.add(value)

        if duplicated:
            value_description = ', '.join([repr(d) for d in duplicated])
            raise ValidationError(f"{message}: {value_description}")


def _iterate_error_messages(prefixes, errors):
    if isinstance(errors, list):
        for index, error in enumerate(errors):
            if isinstance(error, str):
                # Global error on the field collection:
                new_prefixes = prefixes
            else:
                # list or dict of attributes, so nested:
                new_prefixes = [*prefixes, str(index + 1)]

            yield from _iterate_error_messages(new_prefixes, error)
    elif isinstance(errors, dict):
        for field_name, error in errors.items():
            new_prefixes = [*prefixes, humanize_camelcased_string(field_name)]

            yield from _iterate_error_messages(new_prefixes, error)
    else:
        prefix = ' '.join(prefixes)
        message = errors

        yield f"{prefix}: {message}".strip().capitalize()
