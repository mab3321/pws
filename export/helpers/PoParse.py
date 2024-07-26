import re
import pdfplumber
from .helperFuncs import *
from .excelhelper import *
class PoParse:
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

