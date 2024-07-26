from helpers import *

# Path to your PDF file
pdf_path = 'uploads/504844FTY.pdf'  # Update the path to your actual PDF file

import pdfplumber
import re

def extract_details(pdf_path):
    extracted_data = {}

    with pdfplumber.open(pdf_path) as pdf:
        # Only focus on the first page
        first_page = pdf.pages[0]
        text = first_page.extract_text()
        print(text)
        # Use regex to find the relevant information
        # Regex patterns to capture the required information
        # Define the regex pattern to extract the line following "Invoice Number Log No"
        pattern_invoice = r'Invoice Number Log No\n(.+?)\s+(\S+)$'
        pattern_date = r'Document Date Invoice Date\n(.+?)\s+(\S+)$'
        # Search for the pattern in the text
        invoice_match = re.search(pattern_invoice, text, re.MULTILINE)
        date_match = re.search(pattern_date, text, re.MULTILINE)
        
        # Extract the Invoice Number and Log No if found
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
        data = {
            "Invoice Number": invoice_number,
            "Log No": log_no,
            "Document Date": document_date,
            "Invoice Date": invoice_date
        }
        return data

# Extract data from the PDF

# Call the function and store the result
extracted_info = extract_details(pdf_path)

# Print the extracted information
print(extracted_info)
