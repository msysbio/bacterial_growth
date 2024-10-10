def validate_upload(study_template, data_template):
    errors = []

    if len(study_template) == 0:
        errors.append('Missing study template')
    if len(data_template) == 0:
        errors.append("Missing data template")

    if len(errors) > 0:
        return errors

    return []
