import os,time

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

# Function to find HS code
def find_hs_code(description):
    description = description.lower()
    material_category = determine_category(description)

    garment_type = None
    gender_category = None

    if 't-shirt' in description:
        garment_type = 'T-Shirts'
    elif 'shirt' in description:
        garment_type = 'Shirts'
    elif 'pant' in description:
        garment_type = 'Pants'
    elif 'jacket' in description:
        garment_type = 'Jackets'
    elif 'track suit' in description:
        garment_type = 'Track Suits'
    elif 'pullover' in description:
        garment_type = 'Pullovers'

    if 'unisex' in description:
        gender_category = 'Men'
    elif 'men' in description:
        gender_category = 'Men'
    elif 'women' in description:
        gender_category = 'Women'
    print(f"{gender_category} {material_category} {garment_type}")
    if material_category and garment_type and gender_category:
        key = f"{gender_category} {material_category} {garment_type}"
        return hs_codes.get(key)

    return None
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

