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
