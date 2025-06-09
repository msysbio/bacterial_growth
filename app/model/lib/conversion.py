MEASUREMENT_RATIOS = {
    # (Source,   Target):     source * ratio = target
    ('Cells/μL', 'Cells/mL'): 1_000,
    ('CFUs/μL',  'CFUs/mL'):  1_000,
    ('mM',       'μM'):       1_000,
    ('mM',       'nM'):       1_000_000,
    ('mM',       'pM'):       1_000_000_000,
    ('μM',       'nM'):       1_000,
    ('μM',       'pM'):       1_000_000,
    ('nM',       'pM'):       1_000,
}


def convert_measurement_units(
    value,
    source_units,
    target_units,
    mass=None,
):
    if source_units == target_units:
        return value

    if source_units == 'g/L':
        if mass is None:
            return None
        value = (value * 1_000) / float(mass)
        source_units = 'mM'

    if target_units == 'g/L':
        if mass is None:
            return None
        value = (value * float(mass)) / 1_000.0
        target_units = 'mM'

    if source_units == target_units:
        return value

    if (source_units, target_units) in MEASUREMENT_RATIOS:
        ratio = MEASUREMENT_RATIOS[(source_units, target_units)]
        return value * ratio
    elif (target_units, source_units) in MEASUREMENT_RATIOS:
        ratio = MEASUREMENT_RATIOS[(target_units, source_units)]
        return value / ratio
    else:
        return None


def convert_time(time, source, target):
    if source == target:
        return time

    # Convert down to seconds:
    if source == 's':
        seconds = time
    elif source == 'm':
        seconds = round(float(time) * 60)
    elif source == 'h':
        seconds = round(float(time) * 3600)
    elif source == 'd':
        seconds = round(float(time) * 86_400)
    else:
        raise ValueError(f"Conversion from {source} to seconds unsupported")

    # Convert up to what was requested
    if target == 's':
        result = seconds
    elif target == 'm':
        result = seconds / 60
    elif target == 'h':
        result = seconds / 3600
    elif target == 'd':
        result = seconds / 86_400
    else:
        raise ValueError(f"Conversion from seconds to {target} unsupported")

    return round(result, 2)


