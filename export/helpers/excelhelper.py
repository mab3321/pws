import pandas as pd

def get_data_csv(file_path):
    df_full = pd.read_csv(file_path)

    # Find the start and end rows for the desired section
    start_text = "CONSUMPTION OF ACCESSORIES IMPORTED UNDER SRO. 492(I)/ 2009"
    end_text = "HS CODE WISE CONSUMPTION"

    # Locate the rows where these headers are found
    start_row = df_full[df_full.apply(lambda row: row.astype(str).str.contains(start_text, case=False, na=False, regex=False).any(), axis=1)].index.max()
    end_row = df_full[df_full.apply(lambda row: row.astype(str).str.contains(end_text, case=False, na=False, regex=False).any(), axis=1)].index.min()

    data_dict = {}  # Initialize an empty dictionary to handle cases where no data is found

    if pd.notna(start_row) and pd.notna(end_row):
        # Read the specific range of rows, skipping the header row itself
        data = pd.read_csv(file_path, skiprows=int(start_row)+2, nrows=int(end_row-start_row)-2)
        
        # Filter only the required columns by names
        required_columns = ['B/E No', 'PER UNIT VALUE','Now Consume']
        
        # Check if the required columns are in the data
        if set(required_columns).issubset(data.columns):
            filtered_data = data[required_columns]
            # Filter out rows where 'NOW CONSUMED' is NaN or 0
            filtered_data = filtered_data[filtered_data['Now Consume'].notna() & (filtered_data['B/E No'].notna()) & (filtered_data['Now Consume'] != 0)]
            
            # Convert the DataFrame to a dictionary
            data_dict = filtered_data.to_dict(orient='records')  # 'records' creates a list of dictionaries for each row
            return data_dict
            # Display the filtered DataFrame in tabular form (optional, for visual confirmation in Jupyter)
            # display(filtered_data)
    else:
        print("Headers not found in the file")
        raise Exception("Table not found in the file")


