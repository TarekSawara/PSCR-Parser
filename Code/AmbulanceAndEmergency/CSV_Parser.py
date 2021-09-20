import sxl
from tabulate import tabulate

from Code.AmbulanceAndEmergency.CSVNumberOfStaffAndVolunteersSheet import CSVNumberOfStaffAndVolunteersSheet
from Code.AmbulanceAndEmergency.CSVNumberOfStaffAndVolunteersSheetArabic import CSVNumberOfStaffAndVolunteersSheetArabic
from Code.AmbulanceAndEmergency.NumberOfBeneficiaries import NumberOfBeneficiaries


class CSV_Parser:
    SHEETS_TO_CLASS_TRANSLATE = {
        "عدد المنتفعين": NumberOfBeneficiaries,
        "عدد العاملين والمتطوعين": CSVNumberOfStaffAndVolunteersSheetArabic,
        "Sheet4": CSVNumberOfStaffAndVolunteersSheet,
    }

    # "بناء قدرات المتطوعين ",
    # "بناء قدرات العاملين"]

    def __init__(self, filePath, summary_create_path=None, summaryMode=False, df=None):

        if df is None:
            wb = sxl.Workbook(filePath)
            sheetName = list(wb.sheets.keys())[0]
            self.df1 = self.SHEETS_TO_CLASS_TRANSLATE[sheetName](filePath, sheetName=sheetName,
                                                                 addDate=True, info=False, isSummary=summaryMode).df
        elif (summaryMode and summary_create_path):
            wb = sxl.Workbook(filePath)
            sheetName = list(wb.sheets.keys())[0]
            self.SHEETS_TO_CLASS_TRANSLATE[sheetName](filePath, summary_create_path=summary_create_path,
                                                      sheetName=sheetName, df=df, isSummary=summaryMode)
            return

    def display(self):
        print(tabulate(self.df1, headers='keys', tablefmt='psql'))
