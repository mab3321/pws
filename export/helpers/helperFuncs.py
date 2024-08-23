import os,time
from PyPDF2 import PdfMerger
import pdfplumber
import re
from fuzzywuzzy import process
# selenium imports
from selenium.common.exceptions import StaleElementReferenceException
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import Select

from .constants import *
# Function to wait for the page to load completely
import os
import shutil

# Function to determine material category
def determine_category(description):
    match = re.search(r'(\d+)%\s+(\w+)', description)
    if match:
        percentage = int(match.group(1))
        if percentage >= 80:
            return '100%'
        else:
            return '80/20%'
    return None

def csv_path_of_invoice(directory, invoice_number):
    print(f"Searching for CSV file for invoice number {invoice_number} in {directory}...")
    for root, _, files in os.walk(directory):
        for file in files:
            print(file)
            if file.endswith('.csv') and str(invoice_number) in file:
                file_path = os.path.join(root, file)
                return file_path
    raise FileNotFoundError(f"No CSV file found for invoice number {invoice_number}.")
def extract_text_after_number(text):
    pattern = re.compile(r'\d{5,}\s+(.*)')
    match = pattern.search(text)
    if match:
        return match.group(1)
    else:
        return None
# Function to find HS code
def find_hs_code(description):
    description = description.lower().strip().replace('\n', '')
    print(description)
    material_category = determine_category(description)

    garment_type = None
    gender_category = None
    if ('polyester' in description) and ('100' in description):
        if 'suit' in description:
            garment_type = 'Polyester Suits'
        elif 'jacket' in description:
            garment_type = 'Polyester Jackets'
        elif 'pant' in description:
            garment_type = 'Polyester Pants'
        elif 'skirt' in description:
            garment_type = 'Polyester Skirts'
        elif 'pullover' in description:
            garment_type = 'Polyester Pullovers'
    elif 'crocheted' in description:
        garment_type = 'Crocheted'
    elif 't-shirt' in description or 't shirt' in description:
        garment_type = 'T-Shirts'
    elif 'pes shirt' in description:
        garment_type = 'PES Shirts'
    elif 'shirt' in description:
        garment_type = 'Shirts'
    elif 'pant' in description or 'shorts' in description:
        garment_type = 'Pants'
    elif 'jacket' in description:
        garment_type = 'Jackets'
    elif 'track suit' in description:
        garment_type = 'Track Suits'
    elif 'suit' in description:
        garment_type = 'Suits'
    elif 'pullover' in description:
        garment_type = 'Pullovers'

    if 'unisex' in description:
        gender_category = 'Women'
    elif 'women' in description or 'ladies' in description or 'girl' in description:
        gender_category = 'Women'
    elif 'men' in description or 'gentle' in description or 'boy' in description or 'kid' in description:
        gender_category = 'Men'
    
    print(f"{gender_category} {material_category} {garment_type}")
    if material_category and garment_type and gender_category:
        key = f"{gender_category} {material_category} {garment_type}"
        return hs_codes.get(key)

    return None
def categorize_invoice(invoice):
    if invoice[0].isalpha():
        return 'non_local'
    elif invoice[0].isdigit():
        return 'local'
    else:
        raise Exception(f"{invoice } Does not belong to any category .")
def extract_files():
    current_dir = os.getcwd()
    uploads_dir = os.path.abspath(os.path.join(current_dir, os.pardir, 'uploads'))
    
    pl_pdf_path = None
    fty_pdf_path = None
    csv_path = None

    for filename in os.listdir(uploads_dir):
        if filename.endswith('.pdf') or filename.endswith('.csv'):
            old_filepath = os.path.join(uploads_dir, filename)
            new_filename = filename.replace('-', '')
            new_filepath = os.path.join(uploads_dir, new_filename)
            
            # Rename file to remove dashes
            shutil.move(old_filepath, new_filepath)
            
            # Assign the renamed file to the appropriate variable
            if 'fty' in new_filename.lower() and new_filename.endswith('.pdf'):
                fty_pdf_path = new_filepath
            elif 'pl' in new_filename.lower() and new_filename.endswith('.pdf'):
                pl_pdf_path = new_filepath
            elif new_filename.endswith('.csv'):
                csv_path = new_filepath

    # Check if the required files were found and assigned
    if pl_pdf_path and fty_pdf_path and csv_path:
        print(f"PL PDF Path: {pl_pdf_path}")
        print(f"FTY PDF Path: {fty_pdf_path}")
        print(f"CSV Path: {csv_path}")
        # Return the paths for further use
        return pl_pdf_path, fty_pdf_path, csv_path
    else:
        print("Error: Could not find all required files.")
        return None, None, None

def extract_files_club_single(single_path=None):
    if not single_path:
        current_dir = os.getcwd()
        uploads_dir = os.path.abspath(os.path.join(current_dir, os.pardir, 'multi','multisingle'))
    else:
        uploads_dir = os.path.abspath(single_path)
    # Check if the directory is empty
    if not os.listdir(uploads_dir):
        print("Directory is empty.")
        return None, None, None
    pl_pdf_path = None
    fty_pdf_path = None
    csv_path = None

    for filename in os.listdir(uploads_dir):
        if filename.endswith('.pdf') or filename.endswith('.csv'):
            old_filepath = os.path.join(uploads_dir, filename)
            new_filename = filename.replace('-', '')
            new_filepath = os.path.join(uploads_dir, new_filename)
            
            # Rename file to remove dashes
            shutil.move(old_filepath, new_filepath)
            
            # Assign the renamed file to the appropriate variable
            if 'fty' in new_filename.lower() and new_filename.endswith('.pdf'):
                fty_pdf_path = new_filepath
            elif 'pl' in new_filename.lower() and new_filename.endswith('.pdf'):
                pl_pdf_path = new_filepath
            elif new_filename.endswith('.csv'):
                csv_path = os.path.dirname(os.path.abspath(new_filepath))

    # Check if the required files were found and assigned
    if pl_pdf_path and fty_pdf_path and csv_path:
        print(f"PL PDF Path: {pl_pdf_path}")
        print(f"FTY PDF Path: {fty_pdf_path}")
        print(f"CSV Path: {csv_path}")
        # Return the paths for further use
        return pl_pdf_path, fty_pdf_path, csv_path
    else:
        print("Error: Could not find all required files.")
        return None, None, None

def process_duty_drawback(driver,description):
    description = description.lower().strip().replace('\n', '')
    table = WebDriverWait(driver, 100).until(
            EC.presence_of_element_located((By.ID, "ctl00_ContentPlaceHolder2_ItemsInfoDetailUc1_pnldutydrawback"))
        )

    # Find all rows in the table body
    rows = table.find_elements(By.TAG_NAME, "tr")

    # Iterate through the rows, skipping the header
    for row in rows[2:]:
        cells = row.find_elements(By.TAG_NAME, "td")
        if 'dye' in description and 'dyed or printed' in cells[1].text.lower():
            cells[0].click()
            return True
        elif 'white' in description and ('t-shirt' in description or 't shirt' in description) and 'bleached blended' in cells[1].text.lower():
            cells[0].click()
            return True
        elif '100' in description and 'polyester' in description and 'grey blended' in cells[1].text.lower():
            cells[2].click()
            return True
    else:
        row = rows[2]
        cells = row.find_elements(By.TAG_NAME, "td")
        cells[0].click()
        return True

def extract_files_club_po(po_path=None):
    if not po_path:
        current_dir = os.getcwd()
        uploads_dir = os.path.abspath(os.path.join(current_dir, os.pardir, 'multi','multipos'))
    else:
        uploads_dir = os.path.abspath(po_path)  
    # Check if the directory is empty
    if not os.listdir(uploads_dir):
        print("Directory is empty.")
        return None, None, None
    pl_pdf_path = None
    fty_pdf_path = None
    desc_path = None
    csv_path = None
    for filename in os.listdir(uploads_dir):
        if filename.endswith('.pdf') or filename.endswith('.xlsx') or filename.endswith('.csv'):
            old_filepath = os.path.join(uploads_dir, filename)
            new_filename = filename.replace('-', '')
            new_filepath = os.path.join(uploads_dir, new_filename)
            
            # Rename file to remove dashes
            shutil.move(old_filepath, new_filepath)
            
            # Assign the renamed file to the appropriate variable
            if 'fty' in new_filename.lower() and new_filename.endswith('.pdf'):
                fty_pdf_path = new_filepath
            elif 'pl' in new_filename.lower() and new_filename.endswith('.pdf'):
                pl_pdf_path = new_filepath
            elif new_filename.endswith('.csv'):
                csv_path = os.path.dirname(os.path.abspath(new_filepath))
            elif new_filename.endswith('.xlsx'):
                desc_path = new_filepath

    # Check if the required files were found and assigned
    if pl_pdf_path and fty_pdf_path and desc_path:
        print(f"PL PDF Path: {pl_pdf_path}")
        print(f"FTY PDF Path: {fty_pdf_path}")
        print(f"CSV Path: {csv_path}")
        # Return the paths for further use
        return pl_pdf_path, fty_pdf_path, csv_path,desc_path
    else:
        print("Error: Could not find all required files.")
        return None, None, None, None

def merge_pdfs(pdf_path1, pdf_path2, output_dir=None):
    merger = PdfMerger()

    # Append the PDFs to be merged
    merger.append(pdf_path1)
    merger.append(pdf_path2)

    # Set the output directory to 'uploads_merged'
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(pdf_path1), 'uploads_merged')
    
    # Ensure the 'uploads_merged' directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Extract the base name of the first PDF file (without extension)
    base_name = os.path.splitext(os.path.basename(pdf_path1))[0]
    
    # Define the output file name and full path
    output_filename = f"{base_name}merged.pdf"
    output_path = os.path.join(output_dir, output_filename)

    # Write the merged PDF to the output path
    with open(output_path, "wb") as output_pdf:
        merger.write(output_pdf)

    merger.close()

    return output_path

def add_data_dictionaries(dict1, dict2):
    """
    Adds values from two dictionaries containing numerical data.
    For the 'invoices' key, it concatenates the values.

    Args:
        dict1 (dict): The first dictionary.
        dict2 (dict): The second dictionary.

    Returns:
        dict: A dictionary with the summed values or concatenated 'invoices'.
    """
    result = {}
    for key in dict1:
        if key in dict2:
            if isinstance(dict1[key], (int, float)) and isinstance(dict2[key], (int, float)):
                result[key] = dict1[key] + dict2[key]
            elif key == 'invoices':
                result[key] = f"{dict1[key]}\n{dict2[key]}"
            else:
                result[key] = dict1[key]
    # Split the original string by newline characters and then by hyphens
    invoices_list = [item.split('-') for item in result.get('invoices').split('\n')]

    # Flatten the list
    invoices_flat = [item for sublist in invoices_list for item in sublist]

    # Initialize an empty list to store the formatted invoice groups
    formatted_invoices = []

    # Group invoices in sets of three
    for i in range(0, len(invoices_flat), 3):
        formatted_invoices.append('-'.join(invoices_flat[i:i+3]))

    # Join the grouped invoices with newline characters
    formatted_output = '\n'.join(formatted_invoices)
    result['invoices'] = formatted_output
    result['date'] = dict1.get('date', dict2.get('date'))
    return result

def toggle_NonDutyPaid(driver : webdriver.Chrome, ):
    image_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "ctl00_ContentPlaceHolder2_NonDutyPaidItemInfoUc1_Image1"))
    )

    # Get the 'src' attribute of the image
    image_src = image_element.get_attribute("src")
    if 'plus' in image_src.lower():
        click_button(driver,'ctl00_ContentPlaceHolder2_NonDutyPaidItemInfoUc1_pnlTitle')
        time.sleep(1)
def toggle_LocalPurchaseItem(driver : webdriver.Chrome, ):
    image_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "ctl00_ContentPlaceHolder2_LocalPurchaseItemEntryInfoUc1_Image1"))
    )

    # Get the 'src' attribute of the image
    image_src = image_element.get_attribute("src")
    if 'plus' in image_src.lower():
        click_button(driver,'ctl00_ContentPlaceHolder2_LocalPurchaseItemEntryInfoUc1_pnlTitle')
        time.sleep(1)
def select_added_item(driver : webdriver.Chrome):
    table = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, 'ctl00_ContentPlaceHolder2_ItemInfoUc1_dgItems'))
)
    rows = table.find_elements(By.TAG_NAME, 'tr')

    # Get the last row (excluding the header row)
    last_row = rows[-2]

    # Find the "Edit" button in the last row and click it
    edit_button = last_row.find_element(By.LINK_TEXT, 'Edit')
    edit_button.click()

def wait_for_page_load(driver, timeout=100):
    # Wait for the updateProgress element's display style to be 'none'
    time.sleep(1)
    WebDriverWait(driver, timeout).until(
        lambda d: d.find_element(By.ID, 'ctl00_upBar_UpdateProgress1').value_of_css_property('display') == 'none'
    )
def get_file_paths(directory):
    if not os.path.isdir(directory):
        print("The specified directory does not exist.")
        return []
    file_paths = []  # List to store full file paths
    for root, directories, files in os.walk(directory):
        for filename in files:
            pdf_ext = filename.split('.')[-1]
            if pdf_ext == 'pdf':
                filepath = os.path.abspath(os.path.join(root, filename))
                file_paths.append(filepath)
    return file_paths

def option_in_dropdown(dropdown, option_text):
    for option in dropdown.options:
        if option.text == option_text:
            return True
    return False

def select_dropdown(driver,id,option_text,by=By.ID):
    while True:
        try:
            dropdown_elem = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((by, id))
            )
            print(f"Found {id} dropdown_elem.")
            dropdown = Select(dropdown_elem)
            # Wait For the Drop Down Items to appear
            WebDriverWait(driver, 100).until(lambda driver: option_in_dropdown(dropdown, option_text))
            dropdown.select_by_visible_text(option_text)
            wait_for_page_load(driver)
            break
        except StaleElementReferenceException:
            print("StaleElementReferenceException: Trying again...")
            time.sleep(2)
        except Exception as e:
            print(f"Exception: {e}")
            raise e
def select_dropdown_by_value(driver,id,value):
    while True:
        try:
            dropdown_elem = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, id))
            )
            print(f"Found {id} dropdown_elem.")
            dropdown = Select(dropdown_elem)
            dropdown.select_by_value(value)
            wait_for_page_load(driver)
            break
        except StaleElementReferenceException:
            print("StaleElementReferenceException: Trying again...")
            time.sleep(2)
        except Exception as e:
            print(f"Exception: {e}")
            raise e
def click_button(driver, id,by=By.ID,pop_up=False):
    while True:
        try:
            button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((by, id))
            )
            print(f"Found {id} button.")
            button.click()
            if not pop_up:
                wait_for_page_load(driver)
            
            break
        except StaleElementReferenceException:
            print("StaleElementReferenceException: Trying again...")
            time.sleep(2)
        except Exception as e:
            print(f"Exception: {e}")
            raise e
    
def write_text(driver, id,text,pop_up=False,by=By.ID):
    while True:
        try:
            elem = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((by, id))
            )
            elem.clear()
            print(f"Found {id} element.")
            elem.send_keys(text)
            elem.send_keys(Keys.ENTER)  # Send the ENTER key
            time.sleep(1)
            if not pop_up:
                wait_for_page_load(driver)
            break
        except StaleElementReferenceException:
            print("StaleElementReferenceException: Trying again...")
            time.sleep(2)
        except Exception as e:
            print(f"Exception: {e}")
            raise e

def write_date(driver, id, text, by=By.ID):
    while True:
        try:
            elem = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((by, id))
            )
            # Use JavaScript to set the value directly
            driver.execute_script(f"arguments[0].value = '{text}';", elem)
            # Trigger any event listeners if necessary
            # driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", elem)
            print(f"Found {id} element and set value to {text}.")
            time.sleep(1)
            wait_for_page_load(driver)
            break
        except StaleElementReferenceException:
            print("StaleElementReferenceException: Trying again...")
            time.sleep(2)
        except Exception as e:
            print(f"Exception: {e}")
            raise e
def extract_text(driver, id,by=By.ID):
    while True:
        try:
            elem = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((by, id))
            )
            text = elem.get_attribute('value')
            return text
        except StaleElementReferenceException:
            print("StaleElementReferenceException: Trying again...")
            time.sleep(2)
        except Exception as e:
            print(f"Exception: {e}")
            raise e

def extract_inner_text(driver, id,by=By.ID):
    while True:
        try:
            elem = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((by, id))
            )
            text = elem.text
            return text
        except StaleElementReferenceException:
            print("StaleElementReferenceException: Trying again...")
            time.sleep(2)
        except Exception as e:
            print(f"Exception: {e}")
            raise e

def checkbox(driver,id,by=By.ID):
    # Wait until the checkbox is present
    while True:
        try:
            checkbox = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((by, id))
            )
            print("Found checkbox.")
            # Check if the checkbox is selected
            if not checkbox.is_selected():
                checkbox.click()
                wait_for_page_load(driver)
                print(f"Checkbox {id} checked.")
            else:
                print(f"Checkbox {id} already checked.")
            break
        except StaleElementReferenceException:
            print("StaleElementReferenceException: Trying again...")
            time.sleep(2)
        except Exception as e:
            print(f"Exception: {e}")
            raise e
# Function to extract relevant data from text (non-table data)
def extract_totals_from_text(page):
    # Extract text from the page
    # Define a regex pattern to find lines with the format: Key Value
    pattern = re.compile(r"Total (\w+(?: \w+)*) (\d{1,3}(?:,\d{3})*\.?\d*)")

    text = page.extract_text()
    if text:
        # Use the regex pattern to find all matches in the text
        matches = pattern.findall(text)
        # Convert matches to a dictionary, removing commas from numbers and converting them to appropriate types
        data_dict = {match[0]: float(match[1].replace(',', '')) for match in matches}
        return data_dict
    else:
        return {}


def final_table(pdf_path):
    # Open the PDF file
    with pdfplumber.open(pdf_path) as pdf:
        # Determine the last two pages
        last_two_pages = pdf.pages[-2:]  # Gets the last two pages
        combined_totals = {}
        
        # Extract relevant totals from the last two pages and combine them into a single dictionary
        for page in last_two_pages:
            totals_dict = extract_totals_from_text(page)
            combined_totals.update(totals_dict)  # Update the combined dictionary with the current page's dictionary
        
        # Print the combined dictionary with data from the last two pages
        return combined_totals

def extract_notes_from_pdf(pdf_path):
    # Open the PDF file
    with pdfplumber.open(pdf_path) as pdf:
        # Initialize an empty string to collect notes
        notes = ""
        # Iterate through each page in the PDF
        for page in pdf.pages:
            text = page.extract_text()
            
            # Check if the text contains "Notes"
            if "Notes" in text:
                # Define a regex pattern to find text following "Notes" until the first new line
                pattern = re.compile(r"Notes\n(.+?)(?=\n)")
                
                # Search the text for the pattern
                match = pattern.search(text)
                
                if match:
                    notes = match.group(1)
                    break  # Assuming you only need the first occurrence

    return notes

