import re
import pdfplumber
from .helperFuncs import *
from .excelhelper import *

class MultiSingleParse:
    def __init__(self,path,csv_path):
        self.pdf_path = path
        self.csv_path = csv_path
        self.pdf = None
        self.text = ''
        self.extracted_data = {}
        self.invoice_number = None
        self.log_no = None
        self.read_pdf()
        self.parse_text()
        self.extract_details()
    def read_pdf(self):
        self.pdf =pdfplumber.open(self.pdf_path)

    def parse_text(self):
        all_text = []
        for page in self.pdf.pages:
            all_text.append(page.extract_text())
        self.text = "\n".join(all_text)

    def extract_details(self):
        
        self.data_from_each_page()
        self.extracted_data['final_table'] = self.summarize_data(self.extracted_data['extracted_data'])
    def data_from_top_box(self,page):
        text = page.extract_text()
        pattern_invoice = r'Invoice Number Log No\n(.+?)\s+(\S+)$'
        pattern_date = r'Document Date Invoice Date\n(.+?)\s+(\S+)$'
        invoice_match = re.search(pattern_invoice,text, re.MULTILINE)
        date_match = re.search(pattern_date, text, re.MULTILINE)
        if invoice_match:
            invoice_number = invoice_match.group(1).strip()
            invoice_number = invoice_number.split(' ')[-1]
            log_no = invoice_match.group(2).strip()
        else:
            invoice_number = None
            log_no = None
        
        if date_match:
            document_date = date_match.group(1).strip()
            invoice_date = date_match.group(2).strip()
        else:
            document_date = None
            invoice_date = None
        return invoice_number,log_no,document_date,invoice_date

    def extract_notes_from_page(self, page):
        # Open the PDF file
        text = page.extract_text()
        if "Notes" in text and "Tax Sentence" in text:
            # Define a regex pattern to find text between "Notes" and "Tax Sentence"
            pattern = re.compile(r"Notes\s*(.*?)\s*Tax Sentence", re.DOTALL)
            
            # Search the text for the pattern
            match = pattern.search(text)
            
            if match:
                notes = match.group(1).strip()
                return notes
            else:
                raise Exception("Could not get notes from the page")
        else:
            raise Exception("'Notes' or 'Tax Sentence' not found in the text")
    def summarize_data(self, data):
        final_table = {
            'Quantity': 0.0,
            'Carton': 0.0,
            'Gross Weight': 0.0,
            'Net Weight': 0.0,
            'Net Net Weight': 0.0,
            'PO Net Amount': 0.0,
            'VAT': 0.0,
            'invoices': ''
        }
        
        invoice_numbers = []

        for item in data:
            final_table['Quantity'] += item.get('Quantity', 0.0)
            final_table['Carton'] += item.get('Carton', 0.0)
            final_table['Gross Weight'] += item.get('Gross Weight', 0.0)
            final_table['Net Weight'] += item.get('Net Weight', 0.0)
            final_table['Net Net Weight'] += item.get('Net Net Weight', 0.0)
            final_table['PO Net Amount'] += item.get('PO Net Amount', 0.0)
            final_table['VAT'] += item.get('VAT', 0.0)
            invoice_numbers.append(item.get('invoice_number', ''))

        # Format the invoice numbers
        formatted_invoices = ''
        for i in range(0, len(invoice_numbers), 3):
            formatted_invoices += '-'.join(invoice_numbers[i:i+3])
            if i + 3 < len(invoice_numbers):
                formatted_invoices += '\n'

        final_table['invoices'] = formatted_invoices.strip()
        
        return final_table

    def data_from_each_page(self,):
          # Gets the last two pages
        combined_totals =[]
        # Extract relevant totals from the last two pages and combine them into a single dictionary
        for page in self.pdf.pages:
            invoice_number,log_no,document_date,invoice_date = self.data_from_top_box(page)
            notes = self.extract_notes_from_page(page)
            hs_code = find_hs_code(notes)
            totals_dict = extract_totals_from_text(page)
            totals_dict['hs_code'] = hs_code
            totals_dict['notes'] = notes
            totals_dict['description'] = extract_text_after_number(notes)
            totals_dict['invoice_number'] = invoice_number[-6:]
            csv_path = csv_path_of_invoice(self.csv_path, invoice_number[-6:])
            totals_dict['csv_obj'] = CSVDataExtractor(csv_path)
            totals_dict['log_no'] = log_no
            totals_dict['document_date'] = document_date
            totals_dict['invoice_date'] = invoice_date
            combined_totals.append(totals_dict)  # Update the combined dictionary with the current page's dictionary
        self.extracted_data['extracted_data'] = combined_totals
        # Print the combined dictionary with data from the last two pages
        return True

    def get_invoice_number(self):
        return self.invoice_number

    def get_log_no(self):
        return self.log_no

    def set_text(self, text):
        self.text = text

    def __str__(self):
        return f"Invoice Number: {self.invoice_number}, Log No: {self.log_no}"

class MultiPOParse:
    def __init__(self,path,csv_path,des_path):
        self.des_path = des_path
        self.pdf_path = path
        self.csv_path = csv_path
        self.extracted_data = {}
        self.po_data = []
        self.extract_details()
    def get_item_info(self, po_number):
        """
        Retrieves the 'CTNS' and 'Desc' values for a given PO number from a list of dictionaries.

        Args:
            data_list (list): The list of dictionaries containing PO data.
            po_number (int): The PO number to search for.

        Returns:
            dict: A dictionary with 'CTNS' and 'Desc' for the specified PO number, or None if not found.
        """
        for item in self.po_data:
            if po_number in item:
                return {'CTNS': item[po_number]['CTNS'], 'description': item[po_number]['Desc'], 'hs_code':find_hs_code(item[po_number]['Desc'])}
        return None
    def extract_details(self):
        final_table_list = []
        extracted_data = self.extract_po_numbers_per_invoice(self.pdf_path)
        for invoice_number in extracted_data.keys():
            csv_path = csv_path_of_invoice(self.csv_path, invoice_number[-6:])
            extracted_data[invoice_number]['csv_obj'] = CSVDataExtractor(csv_path)
            final_table_list.append(extracted_data[invoice_number]['totals'])
        
        self.po_data = self.load_and_prepare_data()
        self.extracted_data['po_tables'] = extracted_data
        self.extracted_data['final_table'] = self.summarize_data(final_table_list)
    def summarize_data(self, data):
        final_table = {
            'Quantity': 0.0,
            'Carton': 0.0,
            'Gross Weight': 0.0,
            'Net Weight': 0.0,
            'Net Net Weight': 0.0,
            'PO Net Amount': 0.0,
            'VAT': 0.0,
            'invoices': ''
        }
        
        invoice_numbers = []

        for item in data:
            final_table['Quantity'] += item.get('Quantity', 0.0)
            final_table['Carton'] += item.get('Carton', 0.0)
            final_table['Gross Weight'] += item.get('Gross Weight', 0.0)
            final_table['Net Weight'] += item.get('Net Weight', 0.0)
            final_table['Net Net Weight'] += item.get('Net Net Weight', 0.0)
            final_table['PO Net Amount'] += item.get('PO Net Amount', 0.0)
            final_table['VAT'] += item.get('VAT', 0.0)
            invoice_numbers.append(item.get('invoice_number', ''))

        # Format the invoice numbers
        formatted_invoices = ''
        for i in range(0, len(invoice_numbers), 3):
            formatted_invoices += '-'.join(invoice_numbers[i:i+3])
            if i + 3 < len(invoice_numbers):
                formatted_invoices += '\n'

        final_table['invoices'] = formatted_invoices.strip()
        
        return final_table

    
    def restructure_data_to_dict_list(self,df):
        """
        Restructures the DataFrame into a list of dictionaries, where each dictionary
        contains the 'PO #' as a key and a nested dictionary with 'PCS', 'CTNS', and 'Desc' as values.
        
        Args:
            df (pd.DataFrame): The prepared DataFrame.
            
        Returns:
            list: A list of dictionaries structured as specified.
        """
        data_list = []
        for index, row in df.iterrows():
            po_number = row['PO #']
            details = {
                'PCS': row['PCS'],
                'CTNS': row['CTNS'],
                'Desc': row['Desc']
            }
            data_list.append({po_number: details})
        
        return data_list

    def load_and_prepare_data(self):
        """
        Loads data from an Excel file, ignoring the first column and first row,
        then sets the first row (after ignoring) as the header.
        
        Args:
            file_path (str): The path to the Excel file.
            
        Returns:
            pd.DataFrame: The prepared DataFrame.
        """
        # Load the Excel sheet, skipping the first row and first column
        df = pd.read_excel(self.des_path, sheet_name='Sheet1', header=None)
        
        # Drop the first row and column
        df = df.drop([0], axis=0)  # Drop the first row
        df = df.drop([0], axis=1)  # Drop the first column
        
        # Set the first row (after dropping) as the header
        df.columns = df.iloc[0]
        df = df[1:]
        
        data = self.restructure_data_to_dict_list(df)
        
        return data

    def data_from_top_box(self, page):
        text = page.extract_text()
        pattern_invoice = r'Invoice Number Log No\n(.+?)\s+(\S+)$'
        pattern_date = r'Document Date Invoice Date\n(.+?)\s+(\S+)$'
        invoice_match = re.search(pattern_invoice, text, re.MULTILINE)
        date_match = re.search(pattern_date, text, re.MULTILINE)
        
        if invoice_match:
            invoice_number = invoice_match.group(1).strip().split(' ')[-1]
            invoice_number = invoice_number[-6:]
            log_no = invoice_match.group(2).strip()
        else:
            invoice_number = None
            log_no = None
        
        if date_match:
            document_date = date_match.group(1).strip()
            invoice_date = date_match.group(2).strip()
        else:
            document_date = None
            invoice_date = None

        return invoice_number, log_no, document_date, invoice_date
    
    def extract_totals_from_text(self, pages):
        """
        Extracts totals from the text of the pages.

        Args:
            pages (list): A list of page objects from which to extract totals.

        Returns:
            dict: A dictionary with keys as the names of totals and values as the amounts.
        """
        totals = {}
        
        # Define a regex pattern to find lines with the format: Key Value
        pattern = re.compile(r"Total (\w+(?: \w+)*) (\d{1,3}(?:,\d{3})*\.?\d*)")
        
        for page in pages:
            text = page.extract_text()
            if text:
                # Use the regex pattern to find all matches in the text
                matches = pattern.findall(text)
                # Convert matches to a dictionary, removing commas from numbers and converting them to appropriate types
                for match in matches:
                    key = match[0]
                    value = float(match[1].replace(',', ''))
                    if key in totals:
                        totals[key] += value
                    else:
                        totals[key] = value

        return totals

    def extract_po_numbers_per_invoice(self, pdf_path):
        """
        Extracts PO numbers per invoice number from the PDF and also includes extracted totals.
        
        Args:
            pdf_path (str): The path to the PDF file.

        Returns:
            dict: A dictionary with invoice numbers as keys and another dictionary as value containing 'po_numbers' and 'totals'.
        """
        data_per_invoice = {}
        current_po_numbers = []
        previous_pages = []
        previous_invoice_number = None

        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                # Extract invoice data from the top box
                invoice_number, log_no, document_date, invoice_date = self.data_from_top_box(page)
                if not invoice_number:
                    invoice_number = previous_invoice_number
                
                # Add the current page to the list of previous pages
                previous_pages.append(page)
                # If the invoice number changes, store the collected PO numbers and totals
                if previous_invoice_number and previous_invoice_number != invoice_number:
                    
                    # Extract and accumulate totals from the collected pages
                    # Extract PO numbers if the header contains 'PO No'
                    new_pages = previous_pages[:len(previous_pages)-1]
                    for new_page in new_pages:
                        tables = new_page.extract_tables()
                        for table in tables:
                            if len(table) > 0 and 'PO No' in table[0]:
                                df = pd.DataFrame(table[1:], columns=table[0])
                                current_po_numbers.extend(df['PO No'].dropna().tolist())
                    totals = self.extract_totals_from_text(previous_pages[:len(previous_pages)-1])
                    totals['invoice_number'] = previous_invoice_number
                    data_per_invoice[previous_invoice_number] = {
                        'po_numbers': current_po_numbers,
                        'totals': totals
                    }
                    current_po_numbers = []
                    previous_pages = [previous_pages[len(previous_pages)-1]]

                previous_invoice_number = invoice_number

            # Add the last set of data for the last invoice number
            if previous_invoice_number:
                new_pages = previous_pages
                for new_page in new_pages:
                    tables = new_page.extract_tables()
                    for table in tables:
                        if len(table) > 0 and 'PO No' in table[0]:
                            df = pd.DataFrame(table[1:], columns=table[0])
                            current_po_numbers.extend(df['PO No'].dropna().tolist())
                totals = self.extract_totals_from_text(previous_pages)
                totals['invoice_number'] = previous_invoice_number
                data_per_invoice[previous_invoice_number] = {
                    'po_numbers': current_po_numbers,
                    'totals': totals
                }

        return data_per_invoice
