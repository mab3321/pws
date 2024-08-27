from helpers import *

# Use the function to extract data with the additional HS CODE check
file_path = r"C:\Users\DELL\Downloads\PWSAutomate\EFS-537624.csv"
csv = CSVDataExtractor(file_path)
data = {'DESCRIPTION OF GOODS': ' 100% COTTON YARN ',
  'B/E No/PACKAGE NO/PURCHASE INV#': 'KAPS-FS-97672',
  'PER UNIT VALUE': 3.1,
  'NOW CONSUMED': 20.83}
print(csv.get_analysis_number('6104.2900',data))