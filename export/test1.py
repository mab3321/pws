# selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchWindowException,TimeoutException
from selenium.webdriver.support.ui import Select
import time
import argparse
from helpers import *
import os
from datetime import datetime
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

def setup_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-gpu')
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-software-rasterizer')
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def exemptions(driver: webdriver.Chrome):
    # Add SROs/Exemptions
    click_button(driver=driver,id="ctl00_ContentPlaceHolder2_ItemsInfoDetailUc1_dgExemptions_ctl02_lnkBtnAdd")
    select_dropdown(driver=driver,id="ctl00_ContentPlaceHolder2_ItemsInfoDetailUc1_dgExemptions_ctl02_ddlExemption",option_text = r"SRO803(I)/2006-1-0-0-01/07/2006 ( 0 )")
    click_button(driver=driver,id="ctl00_ContentPlaceHolder2_ItemsInfoDetailUc1_dgExemptions_ctl02_lnkBtnAdd")
    
    # Add another
    click_button(driver=driver,id="ctl00_ContentPlaceHolder2_ItemsInfoDetailUc1_dgExemptions_ctl03_lnkBtnAdd")
    select_dropdown(driver=driver,id="ctl00_ContentPlaceHolder2_ItemsInfoDetailUc1_dgExemptions_ctl03_ddlExemption",option_text = r"SRO575(I)/02-1-0-0-31/08/2002 ( 0 )")
    click_button(driver=driver,id="ctl00_ContentPlaceHolder2_ItemsInfoDetailUc1_dgExemptions_ctl03_lnkBtnAdd")
    

def assessment_purpose(driver: webdriver.Chrome):
    
    # Add Assessment Purpose
    text = extract_text(driver=driver,id="ctl00_ContentPlaceHolder2_ItemsInfoDetailUc1_txtQuantity")
    print(f"Extracted Text is {text}")
    write_text(driver=driver,id="ctl00_ContentPlaceHolder2_ItemsInfoDetailUc1_txtQuantity_Statistical_Purpose",text=text)
    # write_text(driver=driver,id="ctl00_ContentPlaceHolder2_ItemsInfoDetailUc1_txtQuantity_International_Traded",text=text)
    # Now Click 
    click_button(driver=driver,id="ctl00_ContentPlaceHolder2_ItemsInfoDetailUc1_btnCalcExportValue")
    time.sleep(3)
    # write_text(driver=driver,id="ctl00_ContentPlaceHolder2_ItemsInfoDetailUc1_txtActualWeight",text="1002.0000")

def populate_username_passowrd_in_login_form(driver,transaction_id,url, username, password):
    status = False
    error = ''

    try:
        driver.get(url)

        username_input = WebDriverWait(driver, 100).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Enter Username']"))
        )
        password_input = WebDriverWait(driver, 100).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Enter Password']"))
        )

        username_input.send_keys(username)
        password_input.send_keys(password)
        sign_in_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Login')]")
        sign_in_button.click()
        status = True
    except TimeoutException:
        error = f"For transaction_id { transaction_id } Login Page did not Appear."
    except Exception as e:
        error = f"For transaction_id { transaction_id } Error Occured => {str(e)}"
    return status, error
def select_types(driver,transaction_id):
    Create_Export_GD = WebDriverWait(driver, 100).until(
        EC.presence_of_element_located((By.XPATH, "//a[contains(., 'Create Export GD')]"))
    )
    print(f"Found Create_Export_GD.")
    # Perform an action on the input element (e.g., click)
    Create_Export_GD.click()
    select_dropdown(driver=driver,id="ctl00_ContentPlaceHolder2_GdSelectionExport1_ddlConsignmentType",option_text = "Export Facilitation Scheme")
    select_dropdown(driver=driver,id="ctl00_ContentPlaceHolder2_GdSelectionExport1_ddlDeclarationType",option_text = "Export Facilitation Scheme")

    Create_button = WebDriverWait(driver, 100).until(
        EC.presence_of_element_located((By.XPATH, "(//input[@value='Create'])[2]"))
    )
    print(f"Found Create_button.")
    # Perform an action on the input element (e.g., click)
    Create_button.click()
    print(f"Clicked Create_button.")

def select_saved(driver,transaction_id):
    saved_GD = WebDriverWait(driver, 100).until(
        EC.presence_of_element_located((By.ID, "ctl00_ContentPlaceHolder2_lnkExportSaved"))
    )
    print(f"Found saved_GD.")
    saved_GD.click()
    GD = WebDriverWait(driver, 100).until(
        EC.presence_of_element_located((By.ID, "ctl00_ContentPlaceHolder2_dgSaved_ctl02_lbTrackingId"))
    )
    print(f"Found GD.")
    GD.click()
    GD = WebDriverWait(driver, 100).until(
        EC.presence_of_element_located((By.ID, "ctl00_ContentPlaceHolder2_btnSaveTop"))
    )
    print("GD ready")

def select_GDS(driver,transaction_id):
    status = False
    error = ''
    print(f"For transaction_id { transaction_id } Selecting GDS...")
    try:
        traders_button = WebDriverWait(driver, 100).until(
            EC.presence_of_element_located((By.XPATH, "(//*[@id='List of Traders'])[2]"))
        )
        print(f"Found traders_button.")
        traders_button.click()
        iframe = WebDriverWait(driver, 100).until(
            EC.presence_of_element_located((By.XPATH, "(//*[@id='frame'])[1]"))
        )
        driver.switch_to.frame(iframe)
        print(f"iframe Switched.")
        time.sleep(3)
        company_element = WebDriverWait(driver, 100).until(
            EC.presence_of_element_located((By.XPATH, "//td[text()='STYLE TEXTILE (PRIVATE) LTD']/preceding-sibling::td[1]//input[@type='image']"))
        )
        print(f"Found company_element.")
        # Perform an action on the input element (e.g., click)
        company_element.click()
        driver.switch_to.default_content()
        time.sleep(3)
        print(f"Switched to default_content.")
        goods_declaration = WebDriverWait(driver, 100).until(
            EC.presence_of_element_located((By.XPATH, "(//*[@id='Goods Declaration'])[2]"))
        )
        print(f"Found goods_declaration.")
        goods_declaration.click()
        driver.switch_to.frame(iframe)
        select_types(driver,transaction_id)
        # select_saved(driver,transaction_id)
        status = True
    except Exception as e:
        error = f"For transaction_id { transaction_id } Error Occured => {str(e)}"
        print(e)
    return status, error

def fill_form(driver : webdriver.Chrome,transaction_id,data={}):
    status = False
    error = ''
    pl_data = data.get("pl_data")
    fty_data = data.get("fty_data")
    print(f"For transaction_id { transaction_id } Filling the Form...")
    try:
        # Basic Info
        select_dropdown(driver=driver,id="ctl00_ContentPlaceHolder2_BasicInfoUc1_ddlCollectorate",option_text = "Port Qasim (exports), karachi")
        select_dropdown(driver=driver,id="ctl00_ContentPlaceHolder2_BasicInfoUc1_ddlModeOfTransport",option_text = "Inland water Transport")
        
        # Consignor & Consignee Information (Hide)
        write_text(driver, "ctl00_ContentPlaceHolder2_ConsigneeInfoUc1_txtConsignorName", pl_data.get("consignee"))
        write_text(driver, "ctl00_ContentPlaceHolder2_ConsigneeInfoUc1_txtConsignorAddress", pl_data.get("address"))
        
        # GD Information
        select_dropdown(driver=driver,id="ctl00_ContentPlaceHolder2_GdInfoSeaUc_ddlConsignmentMode",option_text = "Part Shipment")
        # SET the BL/AWB No (Invoice No Last Six digits)
        write_text(driver, "ctl00_ContentPlaceHolder2_GdInfoSeaUc_txtBlNo", fty_data.get("extracted_data")[0].get('invoice_number'))
        #  SET the BL/AWB Date (Invoice Date)
        # Parse the date string into a datetime object
        date_object = datetime.strptime(fty_data.get("extracted_data")[0].get('invoice_date'), "%Y-%m-%d")
        write_date(driver, "ctl00_ContentPlaceHolder2_GdInfoSeaUc_txtBlDate_txtDate", date_object.strftime("%d/%m/%Y"))
        #  Select the Port of Shipment dropdown
        select_dropdown(driver=driver,id="ctl00_ContentPlaceHolder2_GdInfoSeaUc_ddlPortOfShipment",option_text = "Port Qasim (exports), karachi")
        #  Select the Destination Country
        select_dropdown(driver=driver,id="ctl00_ContentPlaceHolder2_GdInfoSeaUc_ddlDestinationCountry",option_text = "United States")
        #  Select the Destination Port
        select_dropdown_by_value(driver=driver,id="ctl00_ContentPlaceHolder2_GdInfoSeaUc_ddlPortOfDischarge",value = "41846")
        # Select the Shipping Line
        select_dropdown_by_value(driver=driver,id="ctl00_ContentPlaceHolder2_GdInfoSeaUc_ddlShippingline",value = "66")
        # SET Place of Delivery
        write_text(driver, "ctl00_ContentPlaceHolder2_GdInfoSeaUc_txtPlaceofDelivery", "Long Beach, USA")
        # SET Net Weight (MT)
        net_weight = data.get("final_table").get("Net Weight") / 1000
        write_text(driver, "ctl00_ContentPlaceHolder2_GdInfoSeaUc_txtNetWeight", net_weight)
        # SET Gross Weight
        gross_weight = data.get("final_table").get("Gross Weight") / 1000
        write_text(driver, "ctl00_ContentPlaceHolder2_GdInfoSeaUc_txtGrossWeight", gross_weight)
        # SET Marks
        marks = f"""AS PER SHIPPER \n INVOICE NO.\n{data.get("final_table").get('invoices')}"""
        write_text(driver, "ctl00_ContentPlaceHolder2_GdInfoSeaUc_txtMarks", marks)

        # financials_info
        # Select the PAYMENT TERM dropdown
        select_dropdown(driver=driver,id="ctl00_ContentPlaceHolder2_FinancialsUc1_ddlPaymentTerms",option_text = "Without LC")
        # Select the Bank dropdown
        select_dropdown(driver=driver,id="ctl00_ContentPlaceHolder2_FinancialsUc1_ddlBank",option_text = "MCB BANK LIMITED")
        # Select the Delivery Term dropdown
        select_dropdown(driver=driver,id="ctl00_ContentPlaceHolder2_FinancialsUc1_ddlDeliveryTerm",option_text = "Free On Board (FOB)")
        # Select the Currency dropdown
        select_dropdown(driver=driver,id="ctl00_ContentPlaceHolder2_FinancialsUc1_ddlCurrency",option_text = "United States-US $")
        # SET FOB Value
        write_text(driver, "ctl00_ContentPlaceHolder2_FinancialsUc1_txtFobValue", data.get("final_table").get("PO Net Amount"))

        # supporting_info_fill

        # Select the Shed/Location Code dropdown
        select_dropdown(driver=driver,id="ctl00_ContentPlaceHolder2_SupportingInfoUc1_ddlExaminerGroup",option_text = "M/S. D.P. World Off-Dock Terminal")
        # Select the ddlTerminal dropdown
        select_dropdown(driver=driver,id="ctl00_ContentPlaceHolder2_SupportingInfoUc1_ddlTerminal",option_text = "Qasim International Container Terminal")

        # check_disclaimer
        checkbox(driver,id="ctl00_ContentPlaceHolder2_ExportPolicyDisclaimerUc1_chkExportPolicy")
        checkbox(driver,id="ctl00_ContentPlaceHolder2_ExportPolicyDisclaimerUc1_chkIsSroDisclaimer")

        # Click the Save button
        click_button(driver=driver,id="ctl00_ContentPlaceHolder2_btnSaveBottom")

        print(f"GD Filling Success")
    except Exception as e:
        error = f"For transaction_id { transaction_id } Error Occured => {str(e)}"
        print(e)
    return status, error

def upload_document(driver : webdriver.Chrome,filepath:os.path.join):
    UploadButton = WebDriverWait(driver, 100).until(
        EC.presence_of_element_located((By.XPATH, "//a[@id='ctl00_ContentPlaceHolder2_UploadDocumentUc1_lnkUploadDocument' and text()='Upload Document']"))
    )
    print(f"Found Upload Button.")
    UploadButton.click()
    fileButton = WebDriverWait(driver, 1000).until(
        EC.presence_of_element_located((By.XPATH, "//table[.//span[text()='Attached Document']]//input[@id='ctl00_ContentPlaceHolder2_GdExportUploadDocUc1_GdImportDocUpload_fuDoc']"))
    )
    print("fileButton ready")
    fileButton.send_keys(filepath)
    if 'fty' in str(filepath).lower():
        select_dropdown(driver=driver,id="ctl00_ContentPlaceHolder2_GdExportUploadDocUc1_cmbDocumentType",option_text = "Invoice")
    else:
        select_dropdown(driver=driver,id="ctl00_ContentPlaceHolder2_GdExportUploadDocUc1_cmbDocumentType",option_text = "Packing List")
    UploadDocButton = WebDriverWait(driver, 100).until(
        EC.presence_of_element_located((By.XPATH, "//table[.//span[text()='Attached Document']]//input[@id='ctl00_ContentPlaceHolder2_GdExportUploadDocUc1_btnUpload' and @value='Upload']"))
    )
    print(f"Found Upload DOC Button.")
    UploadDocButton.click()
    
    WebDriverWait(driver, 500).until(
        EC.presence_of_element_located((By.XPATH, "//table[.//span[text()='Customs Office']]//select[@id='ctl00_ContentPlaceHolder2_BasicInfoUc1_ddlCollectorate']"))
    )
    print("GD ready")

def upload_documents(driver : webdriver.Chrome,pdf_path):
    
    for file in pdf_path:
        print(f"Uploading file: {file}")
        upload_document(driver, file)
def fill_container_info(driver : webdriver.Chrome,data={}):
    # Now Click on Container Info

    click_button(driver=driver,id="//table[.//span[text()='Containers Information']]//a[@id='ctl00_ContentPlaceHolder2_ItemsInfoDetailUc1_dgContainer_ctl02_lnkBtnAdd']",by=By.XPATH)

    write_text(driver=driver,id="//table[.//span[text()='Containers Information']]//input[@id='ctl00_ContentPlaceHolder2_ItemsInfoDetailUc1_dgContainer_ctl02_txtContainerNo']",text="STYLE123456",by=By.XPATH)
    quantity = str(data.get('Quantity'))
    write_text(driver=driver,id="//table[.//span[text()='Containers Information']]//input[@id='ctl00_ContentPlaceHolder2_ItemsInfoDetailUc1_dgContainer_ctl02_txtQuantity']",text=quantity,by=By.XPATH)
    cartons = str(data.get('Carton'))
    write_text(driver=driver,id="//table[.//span[text()='Containers Information']]//input[@id='ctl00_ContentPlaceHolder2_ItemsInfoDetailUc1_dgContainer_ctl02_txtNoOfPackages']",text=cartons,by=By.XPATH)
    select_dropdown(driver=driver,id="//table[.//span[text()='Containers Information']]//select[@id='ctl00_ContentPlaceHolder2_ItemsInfoDetailUc1_dgContainer_ctl02_ddlPackageType']",option_text="CARTONS",by=By.XPATH)
    click_button(driver=driver,id="//table[.//span[text()='Containers Information']]//a[@id='ctl00_ContentPlaceHolder2_ItemsInfoDetailUc1_dgContainer_ctl02_lnkBtnAdd']",by=By.XPATH)


def add_item(driver : webdriver.Chrome,transaction_id,data={}):
    print(f"For transaction_id { transaction_id } Adding Item...")
    click_button(driver=driver,id="//a[@id='ctl00_ContentPlaceHolder2_ItemInfoUc1_lnkItems' and text()='Add Items']",by=By.XPATH)
    print("Clicked Add Items")
    write_text(driver, "ctl00_ContentPlaceHolder2_ItemsInfoDetailUc1_txtHsCode", data.get('hs_code'))
    write_text(driver, "ctl00_ContentPlaceHolder2_ItemsInfoDetailUc1_txtDeclaredDescription", data.get("description"))
    select_dropdown_by_value(driver,'ctl00_ContentPlaceHolder2_ItemsInfoDetailUc1_ddlOrigion','586')
    unit_value = (data.get('PO Net Amount')) / (data.get('Quantity'))
    write_text(driver, "ctl00_ContentPlaceHolder2_ItemsInfoDetailUc1_txtUnitValue", unit_value)
    write_text(driver, "ctl00_ContentPlaceHolder2_ItemsInfoDetailUc1_txtActualWeight", data.get('Quantity'))
    # Select Actual Unit now
    select_dropdown(driver=driver,id="ctl00_ContentPlaceHolder2_ItemsInfoDetailUc1_ddlActualWeightUnit",option_text = "NO")
    print("filling the exemptions")
    exemptions(driver)
    # Check	BLEACHED BLENDED GARMENTS, WEARING APPAREL (ALL BLENDS OF POLYESTER STAPLE FIBRE AND COTTON FIBRE).
    checkbox(driver,id="ctl00_ContentPlaceHolder2_ItemsInfoDetailUc1_dgSro_ctl03_chkSro")
    # Now Handel Quantity (for Assessment Purpose)
    time.sleep(5)
    WebDriverWait(driver, 100).until(
        EC.presence_of_element_located((By.XPATH, "//table[.//span[text()='HS Code']]//input[@id='ctl00_ContentPlaceHolder2_ItemsInfoDetailUc1_txtHsCode']"))
    )
    print(f"Now Executing assessment_purpose")
    
    fill_container_info(driver=driver,data=data)
    assessment_purpose(driver)
    # Now Click on Save Button
    click_button(driver=driver,id="ctl00_ContentPlaceHolder2_btnSaveBottom")
    WebDriverWait(driver, 100).until(
        EC.presence_of_element_located((By.ID, "ctl00_ContentPlaceHolder2_BasicInfoUc1_pnlTitle"))
    )
    print("HScode Added")
    return data.get('hs_code')

def process_gd_number_pop_up_492(driver : webdriver.Chrome,data):
            # Store the ID of the original window
    original_window = driver.current_window_handle

    click_button(driver=driver,id="ctl00_ContentPlaceHolder2_NonDutyPaidItemDetailUc1_btnGDLookup")

    # Wait for the new window or tab (assume we know a new window opens here)
    WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))

    # Get the list of all window handles
    windows = driver.window_handles

    # Switch to the new window
    for window in windows:
        if window != original_window:
            driver.switch_to.window(window)
            break

    # Now you can interact with the new window
    # For example, finding an element and interacting with it
    write_text(driver, "txtSearch",data.get('B/E No'),pop_up=True)
    click_button(driver, "btnSearch",pop_up=True)
    time.sleep(5)
    click_button(driver, id="//tr[@class='ItemStyle']//a[@id='dgLookup_ctl02_lbSelect']",by=By.XPATH,pop_up=True)
        # Attempt to close the new window
    try:
        driver.close()
    except NoSuchWindowException:
        print("The new window was already closed.")

    # Switch back to the original window
    driver.switch_to.window(original_window)
    iframe = WebDriverWait(driver, 100).until(
            EC.presence_of_element_located((By.XPATH, "(//*[@id='frame'])[1]"))
        )
    driver.switch_to.frame(iframe)
    # Locate the table
    table = WebDriverWait(driver, 100).until(
            EC.presence_of_element_located((By.ID, "ctl00_ContentPlaceHolder2_NonDutyPaidItemDetailUc1_dgItems"))
        )

    # Find all rows in the table body
    rows = table.find_elements(By.TAG_NAME, "tr")

    # Iterate through the rows, skipping the header
    for row in rows[1:]:
        cells = row.find_elements(By.TAG_NAME, "td")
        if cells:
            unit_value = float(cells[4].text)
            if int(unit_value) == int(data.get('PER UNIT VALUE')):
                select_link = cells[0].find_element(By.TAG_NAME, "a")
                select_link.click()
                time.sleep(2)
                break
    else:
        # select 1st row
        row = rows[1]
        cells = row.find_elements(By.TAG_NAME, "td")
        if cells:
            select_link = cells[0].find_element(By.TAG_NAME, "a")
            print(f"No matching row found in the table for PER UNIT VALUE {data.get('PER UNIT VALUE')} and {data.get('B/E No/PACKAGE NO/PURCHASE INV#')} Selecting 1st row")
            if select_link.is_enabled() and select_link.get_attribute("disabled") is None:
                select_link.click()
            else:
                print("Select Link is not enabled")
                return None
        else:
            return None
    Quantity = float(extract_text(driver, "ctl00_ContentPlaceHolder2_NonDutyPaidItemDetailUc1_txtQuantity"))
    if data.get('Now Consume') < Quantity:
        write_text(driver, "ctl00_ContentPlaceHolder2_NonDutyPaidItemDetailUc1_txtQuantity",data.get('Now Consume'),pop_up=True)
    return True

def process_gd_number_pop_up_957(driver : webdriver.Chrome,data):
            # Store the ID of the original window
    original_window = driver.current_window_handle

    click_button(driver=driver,id="ctl00_ContentPlaceHolder2_NonDutyPaidItemDetailUc1_btnGDLookup")

    # Wait for the new window or tab (assume we know a new window opens here)
    WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))

    # Get the list of all window handles
    windows = driver.window_handles

    # Switch to the new window
    for window in windows:
        if window != original_window:
            driver.switch_to.window(window)
            break

    # Now you can interact with the new window
    # For example, finding an element and interacting with it
    write_text(driver, "txtSearch",data.get('B/E No/PACKAGE NO/PURCHASE INV#'),pop_up=True)
    click_button(driver, "btnSearch",pop_up=True)
    time.sleep(5)
    click_button(driver, id="//tr[@class='ItemStyle']//a[@id='dgLookup_ctl02_lbSelect']",by=By.XPATH,pop_up=True)
        # Attempt to close the new window
    try:
        driver.close()
    except NoSuchWindowException:
        print("The new window was already closed.")

    # Switch back to the original window
    driver.switch_to.window(original_window)
    iframe = WebDriverWait(driver, 100).until(
            EC.presence_of_element_located((By.XPATH, "(//*[@id='frame'])[1]"))
        )
    driver.switch_to.frame(iframe)
    # Locate the table
    table = WebDriverWait(driver, 100).until(
            EC.presence_of_element_located((By.ID, "ctl00_ContentPlaceHolder2_NonDutyPaidItemDetailUc1_dgItems"))
        )

    # Find all rows in the table body
    rows = table.find_elements(By.TAG_NAME, "tr")

    # Iterate through the rows, skipping the header
    for row in rows[1:]:
        cells = row.find_elements(By.TAG_NAME, "td")
        if cells:
            print("The celss text is : ",cells[4].text)
            try:
                unit_value = float(cells[4].text)
                if int(unit_value) == int(data.get('PER UNIT VALUE')):
                    select_link = cells[0].find_element(By.TAG_NAME, "a")
                    select_link.click()
                    time.sleep(2)
                    break
            except ValueError:
                print(f"Skipping row due to non-numeric value: {cells[4].text}")
    else:
        print('In rows')
        # select 1st row
        row = rows[1]
        cells = row.find_elements(By.TAG_NAME, "td")
        if cells:
            select_link = cells[0].find_element(By.TAG_NAME, "a")
            print(f"No matching row found in the table for PER UNIT VALUE {data.get('PER UNIT VALUE')} and {data.get('B/E No/PACKAGE NO/PURCHASE INV#')} Selecting 1st row")
            if select_link.is_enabled() and select_link.get_attribute("disabled") is None:
                select_link.click()
                time.sleep(2)
            else:
                print("Select Link is not enabled")
                return None
        else:
            return None
    Quantity = float(extract_text(driver, "ctl00_ContentPlaceHolder2_NonDutyPaidItemDetailUc1_txtQuantity"))
    if data.get('NOW CONSUMED') < Quantity:
        write_text(driver, "ctl00_ContentPlaceHolder2_NonDutyPaidItemDetailUc1_txtQuantity",data.get('NOW CONSUMED'),pop_up=True)
    hs_code = extract_text(driver, "ctl00_ContentPlaceHolder2_NonDutyPaidItemDetailUc1_txtHsCode")
    return hs_code

def process_analysis_number_pop_up_957(driver : webdriver.Chrome,analysis_number,hs_code):
            # Store the ID of the original window
    original_window = driver.current_window_handle

    click_button(driver=driver,id="ctl00_ContentPlaceHolder2_NonDutyPaidItemDetailUc1_btnAnalysisLookup")

    # Wait for the new window or tab (assume we know a new window opens here)
    WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))

    # Get the list of all window handles
    windows = driver.window_handles

    # Switch to the new window
    for window in windows:
        if window != original_window:
            driver.switch_to.window(window)
            break

    # Now you can interact with the new window
    # For example, finding an element and interacting with it
    write_text(driver, "txtSearch",analysis_number,pop_up=True)
    write_text(driver, "txtInputHSCode",hs_code,pop_up=True)
    click_button(driver, "btnSearch",pop_up=True)
    time.sleep(3)
    click_button(driver, id="//tr[@class='ItemStyle']//a[@id='dgLookupExport_ctl02_lbSelect']",by=By.XPATH,pop_up=True)
        # Attempt to close the new window
    try:
        driver.close()
    except NoSuchWindowException:
        print("The new window was already closed.")

    # Switch back to the original window
    driver.switch_to.window(original_window)
    iframe = WebDriverWait(driver, 100).until(
            EC.presence_of_element_located((By.XPATH, "(//*[@id='frame'])[1]"))
        )
    driver.switch_to.frame(iframe)

def add_excel_data_492(driver : webdriver.Chrome,data):
    
    click_button(driver=driver,id="//a[@id='ctl00_ContentPlaceHolder2_NonDutyPaidItemInfoUc1_lnkItems' and text()='Attach Item']",by=By.XPATH)
    pop_up_492 = process_gd_number_pop_up_492(driver,data)
    if pop_up_492:
        click_button(driver=driver,id="//input[@id='ctl00_ContentPlaceHolder2_btnSaveBottom']",by=By.XPATH)

        WebDriverWait(driver, 100).until(
            EC.presence_of_element_located((By.ID, "ctl00_ContentPlaceHolder2_btnSaveTop"))
        )
        print(f"Element in pop up Added.")
    else:
        print(f"HS Code Not Found for {data.get('B/E No')}")
        # Cancel the present filling
        click_button(driver=driver,id="ctl00_ContentPlaceHolder2_btnCancelBottom")

def add_excel_data_957(driver : webdriver.Chrome,data,analysis_number):
    
    click_button(driver=driver,id="//a[@id='ctl00_ContentPlaceHolder2_NonDutyPaidItemInfoUc1_lnkItems' and text()='Attach Item']",by=By.XPATH)
    hs_code = process_gd_number_pop_up_957(driver,data)
    if hs_code:
        process_analysis_number_pop_up_957(driver,analysis_number=analysis_number,hs_code=hs_code)
        click_button(driver=driver,id="//input[@id='ctl00_ContentPlaceHolder2_btnSaveBottom']",by=By.XPATH)

        WebDriverWait(driver, 100).until(
            EC.presence_of_element_located((By.ID, "ctl00_ContentPlaceHolder2_btnSaveTop"))
        )
        print(f"Element in pop up Added.")
    else:
        print(f"HS Code Not Found for {data.get('B/E No/PACKAGE NO/PURCHASE INV#')}")
        # Cancel the present filling
        click_button(driver=driver,id="ctl00_ContentPlaceHolder2_btnCancelBottom")

def process_492(driver,data):
    for idx,obj in enumerate(data):
        if obj.get('B/E No'):
            add_excel_data_492(driver,data=obj)
def process_957(driver,data,analysis_number):
    for obj in data:
        categorize_invoice('KPPE-PF-197684')
        if categorize_invoice(obj.get('B/E No/PACKAGE NO/PURCHASE INV#')) == 'non_local':
            add_excel_data_957(driver,data=obj,analysis_number=analysis_number)
        else:
            print(f"Local Invoice {obj.get('B/E No/PACKAGE NO/PURCHASE INV#')}")
            add_excel_data_local(driver,data=obj,analysis_number=analysis_number)
def process_localy_purchased_analysis_no_pop_up_957(driver : webdriver.Chrome,analysis_number,hs_code):
            # Store the ID of the original window
    original_window = driver.current_window_handle

    click_button(driver=driver,id="ctl00_ContentPlaceHolder2_LocalPurchaseItemEntryUc1_btnAnalysisLookup")

    # Wait for the new window or tab (assume we know a new window opens here)
    WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))

    # Get the list of all window handles
    windows = driver.window_handles

    # Switch to the new window
    for window in windows:
        if window != original_window:
            driver.switch_to.window(window)
            break

    # Now you can interact with the new window
    # For example, finding an element and interacting with it
    write_text(driver, "txtSearch",analysis_number,pop_up=True)
    write_text(driver, "txtInputHSCode",hs_code,pop_up=True)
    click_button(driver, "btnSearch",pop_up=True)
    time.sleep(3)
    click_button(driver, id="//tr[@class='ItemStyle']//a[@id='dgLookupExport_ctl02_lbSelect']",by=By.XPATH,pop_up=True)
        # Attempt to close the new window
    try:
        driver.close()
    except NoSuchWindowException:
        print("The new window was already closed.")

    # Switch back to the original window
    driver.switch_to.window(original_window)
    iframe = WebDriverWait(driver, 100).until(
            EC.presence_of_element_located((By.XPATH, "(//*[@id='frame'])[1]"))
        )
    driver.switch_to.frame(iframe)

def process_localy_purchased_pop_up_957(driver : webdriver.Chrome,data):
            # Store the ID of the original window
    original_window = driver.current_window_handle

    click_button(driver=driver,id="ctl00_ContentPlaceHolder2_LocalPurchaseItemEntryUc1_btnLocalPurchaseLookup")

    # Wait for the new window or tab (assume we know a new window opens here)
    WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))

    # Get the list of all window handles
    windows = driver.window_handles

    # Switch to the new window
    for window in windows:
        if window != original_window:
            driver.switch_to.window(window)
            break

    # Now you can interact with the new window
    # For example, finding an element and interacting with it
    write_text(driver, "txtSearch",data.get('B/E No/PACKAGE NO/PURCHASE INV#'),pop_up=True)
    click_button(driver, "btnSearch",pop_up=True)
    time.sleep(5)
    click_button(driver, id="//tr[@class='ItemStyle']//a[@id='dgLookup_ctl02_lbSelect']",by=By.XPATH,pop_up=True)
        # Attempt to close the new window
    try:
        driver.close()
    except NoSuchWindowException:
        print("The new window was already closed.")

    # Switch back to the original window
    driver.switch_to.window(original_window)
    iframe = WebDriverWait(driver, 100).until(
            EC.presence_of_element_located((By.XPATH, "(//*[@id='frame'])[1]"))
        )
    driver.switch_to.frame(iframe)
    # Locate the table
    
    table = WebDriverWait(driver, 100).until(
            EC.presence_of_element_located((By.ID, "ctl00_ContentPlaceHolder2_LocalPurchaseItemEntryUc1_dgItems"))
        )

    # Find all rows in the table body
    rows = table.find_elements(By.TAG_NAME, "tr")

    row = rows[1]
    cells = row.find_elements(By.TAG_NAME, "td")
    if cells:
        select_link = cells[0].find_element(By.TAG_NAME, "a")
        print(f"No matching row found in the table for PER UNIT VALUE {data.get('PER UNIT VALUE')} and {data.get('B/E No/PACKAGE NO/PURCHASE INV#')} Selecting 1st row")
        if select_link.is_enabled() and select_link.get_attribute("disabled") is None:
            select_link.click()
            time.sleep(2)
        else:
            print("Select Link is not enabled")
            return None
    else:
        return None
    hs_code = extract_text(driver, "ctl00_ContentPlaceHolder2_LocalPurchaseItemEntryUc1_txtHsCode")
    return hs_code

def add_excel_data_local(driver : webdriver.Chrome,data,analysis_number):
    # Wait until the image is present
    image_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "ctl00_ContentPlaceHolder2_LocalPurchaseItemEntryInfoUc1_Image1"))
    )

    # Get the 'src' attribute of the image
    image_src = image_element.get_attribute("src")
    if 'plus' in image_src.lower():
        click_button(driver,'ctl00_ContentPlaceHolder2_LocalPurchaseItemEntryInfoUc1_pnlTitle')
        time.sleep(1)
    click_button(driver=driver,id="//a[@id='ctl00_ContentPlaceHolder2_LocalPurchaseItemEntryInfoUc1_lnkItems' and text()='Attach Locally Purchase Item']",by=By.XPATH)
    time.sleep(2)
    
    hs_code = process_localy_purchased_pop_up_957(driver,data)
    if hs_code:
        process_localy_purchased_analysis_no_pop_up_957(driver,analysis_number=analysis_number,hs_code=hs_code)
        click_button(driver=driver,id="//input[@id='ctl00_ContentPlaceHolder2_btnSaveBottom']",by=By.XPATH)
        time.sleep(1)
        WebDriverWait(driver, 100).until(
            EC.presence_of_element_located((By.ID, "ctl00_ContentPlaceHolder2_LocalPurchaseItemEntryInfoUc1_lblTitle"))
        )
        print(f"Element in pop up Added.")
    else:
        print(f"HS Code Not Found for {data.get('B/E No/PACKAGE NO/PURCHASE INV#')}")
        # Cancel the present filling
        click_button(driver=driver,id="ctl00_ContentPlaceHolder2_btnCancelBottom")

def Non_Duty_Paid_Info(driver,csv_obj:CSVDataExtractor,hs_code,elem_index):
    click_button(driver=driver,id=f"//a[@id='ctl00_ContentPlaceHolder2_ItemInfoUc1_dgItems_ctl0{elem_index+1}_lbEdit' and text()='Edit']",by=By.XPATH)
    click_button(driver=driver,id="ctl00_ContentPlaceHolder2_NonDutyPaidItemInfoUc1_lblTitle")
    data_492 = csv_obj.table492_data
    data_957 = csv_obj.table957_data

    process_492(driver,data_492)
    analysis_number = csv_obj.get_analysis_number(hs_code)
    process_957(driver,data_957,analysis_number)
    time.sleep(5)
    click_button(driver=driver,id="ctl00_ContentPlaceHolder2_btnSaveBottom")
    WebDriverWait(driver, 100).until(
        EC.presence_of_element_located((By.ID, "ctl00_ContentPlaceHolder2_BasicInfoUc1_pnlTitle"))
    )
def process_multi_single(driver,items_data,prev_idx=0):
    for idx,item_data in enumerate(items_data):
        hs_code = add_item(driver, 1,data=item_data)
        Non_Duty_Paid_Info(driver,item_data.get('csv_obj'),hs_code,elem_index=idx+1+prev_idx)
        print(f"GD Completed For Item : {item_data}")
    return idx
def process_multi_po(driver ,po_obj:MultiPOParse):
    po_tables = po_obj.extracted_data.get('po_tables')
    invoice_nos = po_tables.keys()
    for invoice in invoice_nos:
        items_data = po_tables[invoice].get('po_numbers')
        for idx,item_data in enumerate(items_data):
            print(items_data)
            data_to_send = po_obj.get_item_info(item_data)
            totals = po_tables[invoice].get('totals')
            data_to_send.update(po_tables[invoice].get('totals'))
            print(data_to_send)
            
            hs_code = add_item(driver, 1,data=item_data)
            Non_Duty_Paid_Info(driver,item_data.get('csv_obj'),hs_code,elem_index=idx+1)
            print(f"GD Completed For Item : {item_data}")
    return idx
def main(data):
    try:
        print('hi')
        finalStatus = False
        finalMessage =''
        driver = setup_driver()
        transaction_id = data.get("transaction_id")
        username = data["UserName"]
        passwd = data["Password"]
        url = data["URL"]
        login_form_status = True
        login_form_status, login_form_error = populate_username_passowrd_in_login_form(driver, transaction_id,url, username, passwd)
        if login_form_status:
            # pickle.dump(driver.get_cookies(), open("cookies.pkl", "wb"))
            print(f"For transaction_id { transaction_id } Cookies Done...")
            wait = WebDriverWait(driver, 60)
            # Define a condition to wait for page load (you can customize this)
            page_load_condition = EC.presence_of_element_located((By.ID, "sidebar-container"))
            # Wait until the page is fully loaded
            wait.until(page_load_condition)
            time.sleep(3)
            GD_status, GD_error = select_GDS(driver, transaction_id)
            print(f"GD_status: {GD_status}, GD_error: {GD_error}")
            if GD_status:
                fill_form_status, fill_form_error = fill_form(driver, transaction_id,data=data)
                time.sleep(5)
                print(f"Uploading the documents")
                upload_documents(driver,pdf_path=data.get('pdf_paths'))
                time.sleep(5)
                fty_data = data.get('fty_data')
                po_obj = data.get('po_obj')
                items_data = fty_data.get('extracted_data')
                prev_idx = 0
                prev_idx = process_multi_po(driver,po_obj)
                process_multi_single(driver,items_data,prev_idx)
        else:
            finalMessage = login_form_error

    except Exception as e:
        print(f"For transaction_id { transaction_id } Exception occurred: {e}")
        finalStatus = False
        finalMessage = str(e)
    finally:
        return driver
pl_pdf_path, fty_pdf_path, csv_path = extract_files_club_single()
pl_po_pdf_path, fty_po_pdf_path, csv_po_path,desc_po_path = extract_files_club_po()

fty_parser = MultiSingleParse(fty_pdf_path,csv_path=csv_path)
pl_parser = PlParse(pl_po_pdf_path)
po_parser = MultiPOParse(path=fty_po_pdf_path,csv_path=csv_po_path,des_path=desc_po_path)
pdf_paths = [pl_pdf_path, fty_pdf_path]
final_table_data = add_data_dictionaries(po_parser.extracted_data['final_table'],fty_parser.extracted_data['final_table'])

data = {
    'transaction_id': 1,
    'user_id': 2,
    'URL': 'https://app.psw.gov.pk/app/',
    'UserName': 'CA-01-2688539',
    'Password': 'Express@3833',
    'pdf_paths': pdf_paths,
    'pl_data':pl_parser.extracted_data,
    'fty_data':fty_parser.extracted_data,
    'po_obj':po_parser,
    'final_table':final_table_data,
}
print(fty_parser.extracted_data['extracted_data'][0].get('csv_obj').table492_data)
print(fty_parser.extracted_data['extracted_data'][0].get('csv_obj').table957_data)
print(fty_parser.extracted_data['extracted_data'][0].get('csv_obj').table1_data)
required_keys = list(data.keys())

driver = main(data)
