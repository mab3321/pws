from helpers.ClubParse import *
# Load the new Excel file
desc_path = r"C:\Users\MAB\Downloads\PWSAutomate\multi\508645 DES SHEET.xlsx"

csv_path = r'C:\Users\MAB\Downloads\PWSAutomate\multi'

fty_path = r"C:\Users\MAB\Downloads\PWSAutomate\multi\fty3.pdf"
po = MultiPOParse(fty_path,csv_path,desc_path)
print(po.po_data)

