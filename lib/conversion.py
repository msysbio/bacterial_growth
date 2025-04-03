# TODO (2025-04-03) Test, complete

def convert_time(time, source, target):
    if source == target:
        return time
    elif source == 'h' and target == 's':
        return round(float(time) * 3600)
    elif source == 'm' and target == 's':
        return round(float(time) * 60)
    else:
        raise ValueError(f"Conversion from {source} to {target} unsupported for now")
