import hashlib
import re
import sqlite3
from turtle import pd
import xlrd
import xlsxwriter
from md5hash import md5sum


class FileHelp:
    def __init__(self):
        pass

    @staticmethod
    def fix_file_checksum():
        """
        this func fixes the xl file so there will be complete similarity between this file and decrypted file,basically
        uses parser of xlsx file to prevent human error
        :return: fixed file
        """
        loc = "customers_data.xlsx"
        wb = xlrd.open_workbook(loc)
        sheet = wb.sheet_by_index(0)
        number_of_customers = sheet.nrows
        workbook = xlsxwriter.Workbook('customers_data_fixed.xlsx')
        worksheet = workbook.add_worksheet()

        for i in range(0, number_of_customers):
            message = sheet.cell_value(i, 0)
            kws = re.sub(r'\W+', ' ', message).casefold()
            worksheet.write(i, 0, kws)

        workbook.close()
        return workbook.filename

    @staticmethod
    def turn_file_to_hash(loc):
        wb = xlrd.open_workbook(loc)
        sheet = wb.sheet_by_index(0)
        number_of_customers = sheet.nrows
        workbook = xlsxwriter.Workbook('hased_customers_data.xlsx')
        worksheet = workbook.add_worksheet()
        for i in range(0, number_of_customers):
            " cp1251 stands for standard utf-8 encoding in base64"
            message = md5sum(str.encode(sheet.cell_value(i, 0)))
            worksheet.write(i, 0, message)

        workbook.close()
        return workbook.filename

    @staticmethod
    def md5checksum(fname):
        """ this func turns file content into hex and digist it,this is for the digital signature
        returns hexdigest of all file content.
        """
        md5 = hashlib.md5()
        wb = xlrd.open_workbook(fname)
        sheet = wb.sheet_by_index(0)
        number_of_customers = sheet.nrows

        for i in range(0, number_of_customers):
            " cp1251 stands for standard utf-8 encoding in base64"
            message = sheet.cell_value(i, 0)
            message = bytes(str(message), 'cp1251')
            md5.update(message)

        return md5.hexdigest()

    @staticmethod
    def option_to_upload_file_to_db():
        filename = "customers_data_fixed"
        con = sqlite3.connect(filename + ".db")
        wb = pd.ExcelFile(filename + '.xlsx')
        for sheet in wb.sheet_names:
            df = pd.read_excel(filename + '.xlsx')
            df.to_sql(sheet, con, index=False, if_exists="replace")
        con.commit()
        con.close()
        from xlsxwriter.workbook import Workbook

        workbook = Workbook('output2.xlsx')
        worksheet = workbook.add_worksheet()

        conn = sqlite3.connect('customers_data_fixed.db')
        c = conn.cursor()
        c.execute("select * from sheet1")
        mysel = c.execute("select * from sheet1 ")
        names = list(map(lambda x: x[0], mysel.description))
        for name in names:
            x = name
        worksheet.write(0, 0, x)

        for i, row in enumerate(mysel):
            worksheet.write(i + 1, 0, row[0])
        workbook.close()