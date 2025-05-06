from flask_wtf import FlaskForm
from wtforms.validators import ValidationError

class BaseForm(FlaskForm):
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

    def get_template(self, subclass_name):
        return getattr(self.__class__, subclass_name)()
