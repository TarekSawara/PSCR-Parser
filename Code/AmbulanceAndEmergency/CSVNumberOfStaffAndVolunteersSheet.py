# Load the Pandas libraries with alias 'pd'
from datetime import datetime
from datetime import timedelta

import pandas as pd
import sxl
# importing the modules
from tabulate import tabulate


class Record:
    def __init__(self, filename):
        self.sector = ""
        self.position = ""
        self.gender = ""
        self.total = 0
        self.date = None

    def to_dict(self):
        if (self.date):
            return dict(Sector=self.sector, Position=self.position, Gender=self.gender, Total=self.total,
                        date=self.date)
        return dict(Sector=self.sector, Position=self.position, Gender=self.gender, Total=self.total)

    def __repr__(self) -> str:
        return str(self.to_dict())


class CSVNumberOfStaffAndVolunteersSheet:
    def __init__(self, filename, sheetName, addDate=False, info=False, offset=0, isSummary=False):
        if isSummary == False:
            self.df = self.CSV2DataFrame(filename, sheetName, addDate, info, offset=offset)
        else:
            self.DataFrame2CSV(filename, sheetName, addDate, info, offset=offset)

    @staticmethod
    def CSV2DataFrame(filename, sheetName, addDate=False, info=False, offset=0):
        uploadTime = None
        if (addDate):
            uploadTime = (datetime.today() + timedelta(days=offset)).replace(microsecond=0).isoformat()
        # get headers
        wb = sxl.Workbook(filename)
        ws = wb.sheets.get(sheetName)
        print(sheetName)
        headers = CSVNumberOfStaffAndVolunteersSheet.none_replace(ws.head(3))

        df = pd.read_excel(filename, sheet_name=sheetName, skiprows=[0, 1, 2], header=None, engine='openpyxl')
        df.columns = headers[2]
        # to_append = headers[1]
        # a_series = pd.Series(to_append, index=df.columns)
        # df = df.append(a_series, ignore_index=True)
        if (info):
            print(tabulate(df, headers='keys', tablefmt='psql'))
        df_final = pd.DataFrame()
        for index, row in df.iterrows():
            if 'total' in row[0].lower():
                continue
            section = -1
            records_l = []
            sections = list(set(headers[1][1:-1]))
            startedColumn = sections[1][0]
            sectorColumn = "Service / Specialty"
            for index, column in enumerate(df.columns):

                if headers[1][index] in sections and headers[1][index] != startedColumn:
                    startedColumn = headers[1][index]
                    section += 1
                if (not 'total' in column.lower()):
                    if "female" in column.lower() or "male" in column.lower():
                        record = Record(filename)
                        record.position = "volunteer" if "volunteer" in headers[1][index].lower() else "staff"
                        record.sector = row[sectorColumn]
                        record.gender = "female" if "female" in column.lower() else "male"
                        record.total = row[column][section]
                        if (uploadTime):
                            record.date = uploadTime
                        records_l.append(record)
                        df_final = df_final.append(record.to_dict(), ignore_index=True)
                    if "service" in headers[1][index].lower():
                        sectorColumn = column

        if (info):
            print(tabulate(df_final, headers='keys', tablefmt='psql'))

        return df_final

    @staticmethod
    def none_replace(ls):
        res = ls[:]
        for r_i in range(len(ls), 0, -1):
            for c_i in range(len(ls[r_i - 1])):  # skipp last column which is about total
                cellVal = res[r_i - 1][c_i - 1]
                leftCellVal = res[r_i - 1][c_i - 2] if c_i > 1 else None
                upCellVal = res[r_i - 2][c_i - 1] if r_i > 1 else None
                res[r_i - 1][c_i - 1] = cellVal if cellVal is not None else upCellVal if upCellVal else leftCellVal
        return ls
