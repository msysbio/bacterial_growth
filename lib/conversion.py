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
