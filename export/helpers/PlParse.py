import re
import pdfplumber
from .helperFuncs import *
class PlParse:
    def __init__(self,path):
        self.pdf_path = path
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
    def find_hscode(self):
        notes = self.extracted_data.get('notes')
    def parse_text(self):
        all_text = []
        for page in self.pdf.pages:
            all_text.append(page.extract_text())
        self.text = "\n".join(all_text)

    def extract_details(self):
        self.data_from_top_box()
        self.extract_notes_from_pdf()
        self.final_table()
        self.find_hscode()
        self.consignee_info()
    def data_from_top_box(self):
        pattern_invoice = r'Invoice Number Log No\n(.+?)\s+(\S+)$'
        pattern_date = r'Document Date Invoice Date\n(.+?)\s+(\S+)$'
        pattern_dest = r'Destination To Forwarder Ship Mode\n(.+?)\s+(\S+)$'
        invoice_match = re.search(pattern_invoice, self.text, re.MULTILINE)
        date_match = re.search(pattern_date, self.text, re.MULTILINE)
        destination_match = re.search(pattern_dest, self.text,re.MULTILINE)
        if invoice_match:
            invoice_number = invoice_match.group(1).strip()
            invoice_number = invoice_number.split(' ')[-1]
            log_no = invoice_match.group(2).strip()
        else:
            invoice_number = None
            log_no = None
        if destination_match:
            destination_line = destination_match.group(1).strip()
            print(destination_line)
            # Split the line into words
            words = destination_line.split(' ')

            # Concatenate the remaining words back into a single string
            destination = words[0]
        else:
            destination = None
        # Add parsed data to the extracted_data dictionary
        self.extracted_data["Invoice Number"] = invoice_number
        self.extracted_data["Log No"] = log_no
        self.extracted_data["destination"] = destination
        if date_match:
            document_date = date_match.group(1).strip()
            invoice_date = date_match.group(2).strip()
        else:
            document_date = None
            invoice_date = None
        self.extracted_data["Document Date"] = document_date
        self.extracted_data["Invoice Date"] = invoice_date
        self.invoice_number = invoice_number
        self.log_no = log_no
        
    def consignee_info(self):
        pattern_consignee_info = r'Actual Manufacturer Consignee\n(.+?)\nCustomer No Supplier Reference Loading Type'
        # consignee_match = re.search(pattern_consignee, self.text, re.MULTILINE)
        consignee_info = re.search(pattern_consignee_info, self.text, re.DOTALL)
        if consignee_info:
            address = ''
            extracted_text = consignee_info.group(1)
            for line in extracted_text.split('\n'):
                if 'STYLE TEXTILE PVT LTD.' in line:
                    consignee = line.split('STYLE TEXTILE PVT LTD.')[-1]
                    self.extracted_data['consignee'] = consignee
                elif 'KOT LAKHPAT' in line:
                    address += line.split('KOT LAKHPAT')[-1]
                elif '126-3 INDUSTRIAL AREA' in line:
                    address += line.split('126-3 INDUSTRIAL AREA')[-1]
                elif 'Lahore,54770' in line:
                    address += line.split('Lahore,54770')[-1]
                else:
                    address += ''
            self.extracted_data['address'] = address
        

    def extract_notes_from_pdf(self):
    # Open the PDF file
    
        if "Notes" in self.text:
            # Define a regex pattern to find text following "Notes" until the first new line
            pattern = re.compile(r"Notes\n(.+?)(?=\n)")
            
            # Search the text for the pattern
            match = pattern.search(self.text)
            
            if match:
                notes = match.group(1)
                self.extracted_data['notes'] = notes
    def final_table(self,):
        last_two_pages = self.pdf.pages[-2:]  # Gets the last two pages
        combined_totals = {}
        # Extract relevant totals from the last two pages and combine them into a single dictionary
        for page in last_two_pages:
            totals_dict = extract_totals_from_text(page)
            combined_totals.update(totals_dict)  # Update the combined dictionary with the current page's dictionary
        self.extracted_data['final_table'] = combined_totals
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

