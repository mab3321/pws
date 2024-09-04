from helpers import *

# Use the function to extract data with the additional HS CODE check
# file_path = r"C:\Users\DELL\Downloads\PWSAutomate\EFS-537624.csv"
# csv = CSVDataExtractor(file_path)
# print(csv.get_analysis_number('6109.1000',{'DESCRIPTION OF GOODS':'100% COTTON YARN'},csv))
# # hs_code_table = csv.hs_code_wise_tables.get(str(6109.1))
# # main_details = hs_code_table.get('main_details')
# hs_code_table = csv.hs_code_wise_tables['6109.1000']
print(categorize_invoice(' KAPS-FS-54535'))