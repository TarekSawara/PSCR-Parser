# Load the Pandas libraries with alias 'pd'
from datetime import datetime
from datetime import timedelta

import pandas as pd
import sxl
# importing the modules
from tabulate import tabulate

panesStartIndex = 0
panesEndIndex = 4


class Record:
    def __init__(self, filename):
        # if "managment" in filename.lower():
        self.service = ""
        self.targetGroup = ""
        self.gender = ""
        self.ageCategory = ""
        self.total = 0
        self.date = None

    def to_dict(self):
        if (self.date):
            return dict(Service=self.service,
                        targetGroup=self.targetGroup,
                        Gender=self.gender,
                        ageCategory=self.ageCategory,
                        Total=self.total,
                        date=self.date)
        return dict(Service=self.service,
                    targetGroup=self.targetGroup,
                    Gender=self.gender,
                    ageCategory=self.ageCategory,
                    Total=self.total)

    def __repr__(self) -> str:
        return str(self.to_dict())


class NumberOfBeneficiaries:
    def __init__(self, filePath, sheetName, addDate=False, info=False, offset=0, isSummary=False):
        self.df = self.CSV2DataFrame(filePath, sheetName, addDate, info, offset=offset)

    @staticmethod
    def CSV2DataFrame(filename, sheetName, addDate=False, info=False, offset=0):
        uploadTime = None
        if (addDate):
            uploadTime = (datetime.today() + timedelta(days=offset)).replace(microsecond=0).isoformat()
        # get headers
        wb = sxl.Workbook(filename)
        ws = wb.sheets.get(sheetName)
        print(sheetName)
        # ws = wb.sheets[2]  # this gets the first sheet
        headers = NumberOfBeneficiaries.none_replace(ws.head(panesEndIndex))

        df = pd.read_excel(filename, sheet_name=sheetName, skiprows=list(range(panesEndIndex)), header=None,
                           engine='openpyxl')
        if (info):
            print(tabulate(df, headers='keys', tablefmt='psql'))
        df.columns = headers[panesEndIndex - 1]
        # to_append = headers[1]
        # a_series = pd.Series(to_append, index=df.columns)
        # df = df.append(a_series, ignore_index=True)
        if (info):
            print(tabulate(df, headers='keys', tablefmt='psql'))
        # df_final = pd.DataFrame(columns=['Department', 'Position', 'Gender', 'Total'])
        df_final = pd.DataFrame()
        for index, row in df.iterrows():
            if 'total' in row[0].lower():
                continue
            section = -1
            records_l = []
            sections = list(set(headers[1][1:-1]))
            startedColumn = sections[1][0]
            sectorColumn = "service/activity"
            targetGroup = "Na"
            age_dict_total = dict()

            for index, column in enumerate(df.columns):

                if headers[1][index] in sections and headers[1][index] != startedColumn:
                    startedColumn = headers[1][index]
                    sections.remove(headers[1][index])
                    section += 1
                if (not 'total' in column.lower()):
                    if "age categories" in headers[1][index]:
                        age_dict_total[column] = row[column]

                    if "target group" in column.lower():
                        targetGroup = row[column]

                    if "female" in column.lower() or "male" in column.lower():
                        record = Record(filename)
                        record.targetGroup = targetGroup
                        record.service = row[sectorColumn]
                        record.gender = "female" if "female" in column.lower() else "male"
                        record.total = row[column]
                        if (uploadTime):
                            record.date = uploadTime
                        records_l.append(record)
                    if "service" in headers[1][index].lower():
                        sectorColumn = column
            for record in records_l:
                record.ageCategory = age_dict_total
                df_final = df_final.append(record.to_dict(), ignore_index=True)

        if (info):
            print(tabulate(df_final, headers='keys', tablefmt='psql'))

        return df_final

    @staticmethod
    def none_replace(ls):
        res = ls[:]
        for r_i in range(len(ls), 0, -1):
            for c_i in range(len(ls[r_i - 1])):  # skipp last column which is about total
                cellVal = res[r_i - 1][c_i]
                leftCellVal = res[r_i - 1][c_i - 1] if c_i > 0 else None
                upCellVal = None
                temp_r_i = r_i
                while (temp_r_i > 1):
                    upCellVal = res[temp_r_i - 2][c_i]
                    if upCellVal:
                        break
                    else:
                        temp_r_i -= 1
                res[r_i - 1][c_i] = cellVal if cellVal is not None else upCellVal if upCellVal else leftCellVal
        return ls
