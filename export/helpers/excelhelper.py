import pandas as pd
import json
def read_csv_data(file_path):
    """
    Reads the CSV data from the given file path.

    Parameters:
    file_path (str): The path to the CSV file.

    Returns:
    pd.DataFrame: The dataframe containing the CSV data.
    """
    return pd.read_csv(file_path, header=None)

def find_start_row(data, start_text):
    """
    Finds the start row index where the given text is found.

    Parameters:
    data (pd.DataFrame): The dataframe containing the CSV data.
    start_text (str): The text to search for.

    Returns:
    int: The index of the start row.
    """
    return data[data.apply(lambda row: row.astype(str).str.contains(start_text, case=False, na=False, regex=False).any(), axis=1)].index.min()

def is_header_row(row, header_keywords):
    """
    Checks if a row contains the header keywords.

    Parameters:
    row (pd.Series): The row to check.
    header_keywords (list): The list of header keywords.

    Returns:
    bool: True if the row contains the header keywords, False otherwise.
    """
    return all(keyword in row.tolist() for keyword in header_keywords)

def find_header_indices(data, header_keywords):
    """
    Finds the indices of the rows where the header appears.

    Parameters:
    data (pd.DataFrame): The dataframe containing the CSV data.
    header_keywords (list): The list of header keywords.

    Returns:
    list: The list of indices where the header appears.
    """
    return data[data.apply(is_header_row, axis=1, header_keywords=header_keywords)].index.tolist()

def extract_main_details(table):
    """
    Extracts the main details from the second row of the table.

    Parameters:
    table (pd.DataFrame): The dataframe containing the table data.

    Returns:
    dict: The dictionary containing the main details.
    """
    main_details = {k: v for k, v in table.iloc[0].to_dict().items() if pd.notna(v)}
    last_key = list(main_details.keys())[-1]
    main_details["ANALYSIS NUMBER"] = main_details.pop(last_key)
    return main_details

def extract_sub_table(table, sub_table_start_text):
    """
    Extracts the sub-table that starts with the given text.

    Parameters:
    table (pd.DataFrame): The dataframe containing the table data.
    sub_table_start_text (str): The text indicating the start of the sub-table.

    Returns:
    pd.DataFrame: The dataframe containing the sub-table.
    """
    sub_table_start_row = table[table.apply(lambda row: row.astype(str).str.contains(sub_table_start_text, case=False, na=False, regex=False).any(), axis=1)].index.min()

    if pd.isna(sub_table_start_row):
        return pd.DataFrame()  # Return an empty dataframe if the sub-table start text is not found

    # Extract the sub-table starting from one row below the identified start row (to include the header)
    sub_table = table.iloc[sub_table_start_row:].reset_index(drop=True)

    if sub_table.empty:
        return pd.DataFrame()  # Return an empty dataframe if the sub-table is empty

    # Set the first row as header and remove it from the data
    sub_table.columns = sub_table.iloc[0]
    
    sub_table = sub_table[1:].reset_index(drop=True)

    # Remove columns where all elements are NaN
    sub_table = sub_table.dropna(axis=1, how='all')

    return sub_table

def filter_sub_table(data):
    """
    Filters the sub-table to remove records with NaN in the "NOW CONSUMED" field
    and includes only the specified keys.

    Parameters:
    data (dict): The dictionary containing the 'main_details' and 'sub_table'.

    Returns:
    dict: The filtered dictionary with records removed where "NOW CONSUMED" is NaN
          and includes only the specified keys.
    """
    main_details = data['main_details']
    sub_table = data['sub_table']

    # Create a DataFrame from the sub_table
    sub_table_df = pd.DataFrame(sub_table)

    # Filter out rows where "NOW CONSUMED" is NaN
    sub_table_df = sub_table_df[sub_table_df['NOW CONSUMED'].notna()]

    # Specify the required columns
    required_columns = ["NOW CONSUMED", "B/E No", "PER UNIT VALUE"]

    # Ensure the columns are standardized and strip any extra spaces
    sub_table_df.columns = sub_table_df.columns.str.strip()

    # Select only the specified columns
    sub_table_df = sub_table_df[required_columns]

    # Convert the filtered DataFrame back to a list of dictionaries
    filtered_sub_table = sub_table_df.to_dict(orient='records')

    # Return the filtered data
    return {
        'main_details': main_details,
        'sub_table': filtered_sub_table
    }

class CSVDataExtractor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.table1_data = self.extract_table_1()
        self.table492_data = self.extract_table_492()
        self.table957_data = self.extract_table_957()
        
        self.hs_code_wise_tables = self.extract_hs_code_wise_tables()

    def get_analysis_number(self,hs_code):
        for entry in self.table1_data:
            if entry['HS CODE:'] == hs_code:
                return entry['ANALYSIS NO:']
        return None
    def extract_table_1(self):
        # Load the CSV file
        data = pd.read_csv(self.file_path, header=None)
        
        # Find the row where HS CODE starts
        hs_code_row_index = data[data.iloc[:, 0] == 'HS CODE:'].index[0]
        
        # Extract column headers from the row where HS CODE is found
        column_headers = data.iloc[hs_code_row_index, 1:].tolist()
        
        # Rows of interest
        rows_of_interest = ['HS CODE:', 'DESCRIPTION:', 'CTN PCS', 'POLSTER PCS', 'WHITE', 'TOTAL PCS', 'N N WEIGHT:', 'ANALYSIS NO:']
        
        # Extract the rows data
        rows_data = {}
        for row_name in rows_of_interest:
            row_index = data[data.iloc[:, 0] == row_name].index[0]
            rows_data[row_name] = data.iloc[row_index, 1:].tolist()
        
        # Create a list to hold the formatted data
        formatted_data = []
        for col_index in range(len(column_headers)):
            col_data = {row: rows_data[row][col_index] for row in rows_of_interest}
            # Only include entries where 'HS CODE:' is not NaN
            if pd.notna(col_data['HS CODE:']):
                formatted_data.append(col_data)
        
        return formatted_data

    def extract_table_492(self):
        df_full = pd.read_csv(self.file_path)

        # Find the start and end rows for the desired section
        start_text = "CONSUMPTION OF ACCESSORIES IMPORTED UNDER SRO. 492(I)/ 2009"
        end_text = "HS CODE WISE CONSUMPTION"

        # Locate the rows where these headers are found
        start_row = df_full[df_full.apply(lambda row: row.astype(str).str.contains(start_text, case=False, na=False, regex=False).any(), axis=1)].index.max()
        end_row = df_full[df_full.apply(lambda row: row.astype(str).str.contains(end_text, case=False, na=False, regex=False).any(), axis=1)].index.min()

        data_dict = {}  # Initialize an empty dictionary to handle cases where no data is found

        if pd.notna(start_row) and pd.notna(end_row):
            # Read the specific range of rows, skipping the header row itself
            data = pd.read_csv(self.file_path, skiprows=int(start_row)+2, nrows=int(end_row-start_row)-2)
            
            # Filter only the required columns by names
            required_columns = ['B/E No', 'PER UNIT VALUE','Now Consume']
            
            # Check if the required columns are in the data
            if set(required_columns).issubset(data.columns):
                filtered_data = data[required_columns]
                # Filter out rows where 'NOW CONSUMED' is NaN or 0
                filtered_data = filtered_data[filtered_data['Now Consume'].notna() & (filtered_data['B/E No'].notna()) & (filtered_data['Now Consume'] != 0)]
                
                # Convert the DataFrame to a dictionary
                data_dict = filtered_data.to_dict(orient='records')  # 'records' creates a list of dictionaries for each row
        else:
            print("Headers not found in the file")
            raise Exception("Table not found in the file")

        return data_dict

    def extract_table_957(self):
        df_full = pd.read_csv(self.file_path, header=None)

        # Find the start and end rows for the desired section
        start_text = "CONSUMPTION OF RAW MATERIAL  IMPORTED & LOCALY PROCURED  UNDER SRO 957 (I) 2021 DATED. 30-JULY-2021(EFS-EXPORT FACILTAION SCHEME)"
        end_text = "CONSUMPTION OF ACCESSORIES IMPORTED UNDER SRO. 492(I)/ 2009"

        # Locate the rows where these headers are found
        start_row = df_full[df_full.apply(lambda row: row.astype(str).str.contains(start_text, case=False, na=False, regex=False).any(), axis=1)].index.max()
        end_row = df_full[df_full.apply(lambda row: row.astype(str).str.contains(end_text, case=False, na=False, regex=False).any(), axis=1)].index.min()

        data_dict = []  # Initialize an empty list to store the data

        if pd.notna(start_row) and pd.notna(end_row):
            # Read the specific range of rows, skipping the header row itself
            data = pd.read_csv(self.file_path, skiprows=int(start_row)+1, nrows=int(end_row-start_row)-2)
            
            # Extract the headers
            headers = data.columns.tolist()
            
            # Convert headers to strings and strip any leading/trailing spaces
            headers = [str(header).strip() for header in headers]
            
            # Set the new headers
            data.columns = headers
            
            # Extract the relevant columns
            required_columns = ['B/E No/PACKAGE NO/PURCHASE INV#', 'PER UNIT VALUE', 'NOW CONSUMED']
            data = data[required_columns]
            
            # Filter out rows where 'NOW CONSUMED' is NaN or 0
            data = data[data['NOW CONSUMED'].notna() & (data['NOW CONSUMED'] != 0)]
            
            # Convert the DataFrame to a list of dictionaries
            data_dict = data.to_dict(orient='records')
            
            return data_dict
        else:
            print("Headers not found in the file")
            raise Exception("Table 957 not found in the file")
    
    def extract_hs_code_wise_tables(self):
        
        """
        Extracts and formats the tables from the CSV file.

        Parameters:
        file_path (str): The path to the CSV file.

        Returns:
        dict: The dictionary containing the formatted tables.
        """
        # Read the CSV data
        df_full = read_csv_data(self.file_path)

        # Define the header keywords
        header_keywords = ["HS CODE", "DESCRIPTION", "PIECES", "NET NET WEIGHT"]
        start_text = "HS CODE WISE CONSUMPTION"
        sub_table_start_text = "CONSUMPTION OF RAW MATERIAL  IMPORTED UNDER SRO 957 (I) 2021 DATED. 30-JULY-2021(EFS-EXPORT FACILTAION SCHEME)"

        # Find the start row
        start_row = find_start_row(df_full, start_text)
        if pd.isna(start_row):
            raise Exception("Start header 'HS CODE WISE CONSUMPTION' not found in the file")

        # Read the data starting after the "HS CODE WISE CONSUMPTION" row
        data = pd.read_csv(self.file_path, skiprows=int(start_row) + 1, header=None)

        # Find all the rows where the header appears
        header_indices = find_header_indices(data, header_keywords)
        if not header_indices:
            raise Exception("Header row not found in the file")

        tables = {}
        
        for i in range(len(header_indices)):
            start_index = header_indices[i]
            end_index = header_indices[i + 1] if i + 1 < len(header_indices) else len(data)

            # Extract the table
            table = data.iloc[start_index:end_index].reset_index(drop=True)

            # Set the first row as header
            table.columns = table.iloc[0]
            table = table[1:]

            # Remove rows where all elements are NaN
            table = table.dropna(how='all')

            # Extract the main details from the second row
            main_details = extract_main_details(table)
            
            # Extract the sub-table
            sub_table = extract_sub_table(table, sub_table_start_text)
            sub_table_dict = sub_table.to_dict(orient='records') if not sub_table.empty else []

            # Format the final table dictionary
            hs_code = main_details['HS CODE']
            final_table_dict = {
                "main_details": main_details,
                "sub_table": sub_table_dict
            }
            final_table_dict_filtered = filter_sub_table(final_table_dict)
            # Add the formatted table to the tables dictionary
            tables[hs_code] = final_table_dict_filtered

        return tables
