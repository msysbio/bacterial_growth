from tempfile import NamedTemporaryFile

import openpyxl


def export_to_xlsx(workbook: openpyxl.Workbook) -> bytes:
    temp_file = NamedTemporaryFile(delete=False, suffix='.xlsx')
    workbook.save(temp_file.name)
    temp_file.close()

    with open(temp_file.name, 'rb') as f:
        data = f.read()

    return data
