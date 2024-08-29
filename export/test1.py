from helpers import *

# # Use the function to extract data with the additional HS CODE check
# file_path = r"C:\Users\DELL\Downloads\PWSAutomate\EFS-537624.csv"
# csv = CSVDataExtractor(file_path)
# for table in csv.hs_code_wise_tables:
#   table_data = csv.hs_code_wise_tables[table]
#   print(table_data)

# Examples
print(formatIocoRatio(1.00))
print(formatIocoRatio(0.0234))
print(formatIocoRatio(0.0054))
print(formatIocoRatio(0.01932))
print(formatIocoRatio(0.009))
