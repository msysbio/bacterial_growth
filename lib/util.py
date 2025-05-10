import re
import itertools
import zipfile
from io import BytesIO


def trim_lines(string):
    return "\n".join(
        line.strip()
        for line in string.splitlines()
        if line != ''
    )


def createzip(csv_data: list[tuple[str, bytes]]):
    buf = BytesIO()

    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as csv_zip:
        for (csv_name, csv_bytes) in csv_data:
            csv_zip.writestr(csv_name, csv_bytes)

    buf.seek(0)
    return buf


def group_by_unique_name(collection):
    return {
        name: _one_or_error(name, group)
        for (name, group) in itertools.groupby(collection, lambda c: c.name)
    }


def humanize_camelcased_string(string):
    return re.sub(r'([a-z])([A-Z])', r'\1 \2', string)

def _one_or_error(key, iterator):
    value = next(iterator)
    try:
        next(iterator)
        # If we're here, we have more than one item
        raise ValueError(f"Non-unique key: {key}")
    except StopIteration:
        return value
