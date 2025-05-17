MEASUREMENT_RATIOS = {
    # (Source,   Target):     source * ratio = target
    ('Cells/μL', 'Cells/mL'): 1_000,
    ('mM',       'μM'):       1_000,
    ('mM',       'nM'):       1_000_000,
    ('mM',       'pM'):       1_000_000_000,
    ('μM',       'nM'):       1_000,
    ('μM',       'pM'):       1_000_000,
    ('nM',       'pM'):       1_000,
}


def convert_measurement_units(left_value, left_units, right_value, right_units, mass=None):
    if left_units == 'g/L':
        if not mass: raise ValueError("Can't convert g/L without a mass value")
        left_value = (left_value * 1_000) / mass
        left_units = 'mM'

    if right_units == 'g/L':
        if not mass: raise ValueError("Can't convert g/L without a mass value")
        right_value = (right_value * 1_000) / mass
        right_units = 'mM'

    if left_units == right_units:
        return (left_value, right_value, left_units)

    if (left_units, right_units) in MEASUREMENT_RATIOS:
        ratio = MEASUREMENT_RATIOS[(left_units, right_units)]
        target_units = right_units
        left_value *= ratio
    elif (right_units, left_units) in MEASUREMENT_RATIOS:
        ratio = MEASUREMENT_RATIOS[(right_units, left_units)]
        target_units = left_units
        right_value *= ratio
    else:
        target_units = None

    return (left_value, right_value, target_units)


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


