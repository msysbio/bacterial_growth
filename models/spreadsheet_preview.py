import pandas as pd


def generate_preview(file):
    excel = pd.ExcelFile(file)

    sheets = {
        name: pd.read_excel(excel, engine='openpyxl', sheet_name=name)
        for name in excel.sheet_names
    }

    return sheets
