import re

import xlrd
import xlsxwriter

from RC6 import Coder


class EncryptAndDecryptFile:
    def __init__(self, key, file, new_file):
        self.key = key
        self.file = file
        self.create_new_file = new_file

    def Encrypt(self):
        wb = xlrd.open_workbook(self.file)
        sheet = wb.sheet_by_index(0)
        number_of_customers = sheet.nrows
        workbook = xlsxwriter.Workbook(self.create_new_file)
        worksheet = workbook.add_worksheet()

        for i in range(0, number_of_customers):
            " cp1251 stands for standard utf-8 encoding in base64"
            message = bytes(str(sheet.cell_value(i, 0)), 'cp1251')
            key = bytes(self.key, 'cp1251')
            cipher = Coder()
            bin_massage = cipher.bytesToBin(message)
            bin_key = cipher.bytesToBin(key)
            encription_bin_message = cipher.encription(bin_massage, bin_key)

            worksheet.write(i, 0, encription_bin_message)
        workbook.close()
        return workbook.filename

    def Decrypt(self):
        wb = xlrd.open_workbook(self.file)

        sheet = wb.sheet_by_index(0)

        number_of_customers = sheet.nrows
        workbook = xlsxwriter.Workbook(self.create_new_file)
        worksheet = workbook.add_worksheet()

        for i in range(0, number_of_customers):
            message = sheet.cell_value(i, 0)
            " cp1251 stands for standard utf-8 encoding in base64"
            key = bytes(self.key, 'cp1251')

            cipher = Coder()
            bin_key = cipher.bytesToBin(key)

            decription_bin_message = cipher.decription(message, bin_key)
            decription_message = cipher.binToBytes(decription_bin_message)
            decoded_decription = decription_message.decode("utf-8")

            " change string representation from bytes to readable string"
            kws = re.sub(r'\W+', ' ', decoded_decription).casefold()
            worksheet.write(i, 0, kws)

        workbook.close()
        return workbook.filename
