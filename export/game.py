# Import Helper Functions
import sys, re
from datetime import datetime
from utils.log import SetLogFile,LogPrint
from utils.error_checks_river import contains_username_or_password,contains_not_balance,money_confirmed
from utils.xpath_interaction import wait_and_click_by_xpath, wait_and_input_by_xpath
from utils.BackendResponse import Send_Response
from utils.s3_helper import uplaod_screenshot
from utils.constants.dir_paths_constants import path_to_captcha_images

from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from CaptchaSolver import main as solve_captcha
import os, random
import argparse
from dotenv import load_dotenv
from pathlib import Path
import time, json
import requests

load_dotenv()


def setup_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-gpu')
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-software-rasterizer')
    return webdriver.Chrome(options=chrome_options)


def populate_username_passowrd_in_login_form(driver,transaction_id,url, username, password):
    status = False
    error = ''

    try:
        driver.get(url)

        username_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Login']"))
        )
        password_input = driver.find_element(By.CSS_SELECTOR, "input[placeholder='Password']")

        username_input.send_keys(username)
        password_input.send_keys(password)
        sign_in_button = driver.find_element(By.CSS_SELECTOR, ".btn.btn-block.btn-primary")
        sign_in_button.click()
        try:
            error_message_class_name = ".alert.alert-error"
            error_message = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, error_message_class_name))
        ).text
            error = error_message

        except TimeoutException:
            status = True
            LogPrint(f"For transaction_id { transaction_id } Login Success...")
    except TimeoutException:
        error = f"For transaction_id { transaction_id } Login Page did not Appear Due to Too many requests (Probably website blocked the access.)"
    except Exception as e:
        error = f"For transaction_id { transaction_id } Error Occured => {str(e)}"
    return status, error


def perform_search(driver, transaction_id,player_username,action):
    # Initialize status and message
    status = False
    message = ''
    try:
        script = """var table = document.getElementById("table-accounts");
                    var tableRows = table.getElementsByTagName('tr')
                    var searchQuery = arguments[0];
                    var found = false;
                    var status = 'Not Found';
                    var message = '';
                    var action = arguments[1];

                    // Check if there are rows
                    if (tableRows.length > 0) {
                        // Iterate through the rows
                        for (var i = 1; i < tableRows.length; i++) {
                            var row = tableRows[i];

                            // Access cells within the row
                            var cells = row.getElementsByTagName("td");
                            var buttons = cells[6]
                            // Check the content of the fourth cell (index 3)
                            var fourthCellContent = cells[2].innerText.trim();
                            console.log(fourthCellContent)
                            // Compare with the search query
                            if (fourthCellContent === searchQuery) {
                                if (action === 'redeem'){
                                var buttonToClick = buttons.querySelector('.btn.btn-mini.btn-danger')}
                                else{
                                    var buttonToClick = buttons.querySelector('.btn.btn-mini.btn-primary')}

                                // Click the button
                                if (buttonToClick) {
                                    buttonToClick.click();
                                    status = 'Success';
                                    message = 'Row ' + (i + 1) + ' contains the search query: ' + searchQuery + '. Button clicked!';
                                } else {
                                    message = 'Button not found in the row.';
                                }

                                found = true;
                                break; // Exit the loop after finding the first match
                            }
                        }

                        if (!found) {
                            message = `Player account ${searchQuery} not found.`;
                        }
                    } else {
                        message = 'No rows found.';
                    }

                    return {'status': status, 'message': message};"""

        # Execute the script and retrieve the result
        result = driver.execute_script(script, player_username,action)

        # Output the result
        LogPrint(f" For transaction_id { transaction_id } Status: {result['status']}\nMessage: {result['message']}")
        status = result['status'] == 'Success'
        message = result['message']
        return status, message
    except Exception as e:
        message = f"For transaction_id { transaction_id }  Error Occured => {str(e)}"
        return status, message


def perform_recharge_amount_actions(driver, transaction_id,action,amount):
    status = False
    error_type = None
    message = ''

    try:
        if 'recharge' in action:
            number_input = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID,'modal-deposite-amount' ))
                )

            number_input.send_keys(amount)

            recharge_button = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="submit"][name="yt1"]'))
                )
            recharge_button.click()
            error_message_selector = ".alert.alert-error"
            balance_is_low = False
            try:
                # Wait for the error message to appear
                message = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, error_message_selector))
                ).text

                if contains_not_balance(message):
                    balance_is_low = True
                    LogPrint(f"For transaction_id { transaction_id } Leaving Now... Reason : {message}")
                    message = message
                    error_type = 'LOW_BALANCE'
                    return status,message, error_type
            except TimeoutException:
                pass

            if not balance_is_low:
                # Click the cross button of reciept, New Feature Added Recently.
                try:
                    error_message_selector = ".alert.alert-success"
                    try:
                        # Wait for the error message to appear
                        message = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, error_message_selector))
                        ).text

                        if money_confirmed(message):
                            LogPrint(f"For transaction_id { transaction_id } Recharge Success.")
                            status = True
                    except TimeoutException:
                        pass

                except TimeoutException:
                    message = "Receipt did not Appear."
        elif 'redeem' in action:
            number_input = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID,'modal-withdrawal-amount' ))
                )
            number_input.clear()
            number_input.send_keys(amount)
            redeem_button = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="submit"][name="yt3"]'))
                )
            redeem_button.click()
            error_message_selector = ".alert.alert-error"
            success_message_selector = '.alert.alert-success'
            try:
                # Wait for the error message to appear
                message = WebDriverWait(driver, 10).until(
                            EC.any_of(
                                EC.presence_of_element_located((By.CSS_SELECTOR, error_message_selector)),
                                EC.presence_of_element_located((By.CSS_SELECTOR, success_message_selector)))
                        ).text

                if 'enough credits on' in message:
                    balance_is_low = True
                    LogPrint(f"For transaction_id { transaction_id } Leaving Now... Reason : {message}")
                    error_type = 'LOW_BALANCE'
                    return status,message, error_type
                elif 'added' in message:
                    response = f"{action} Success."
                    LogPrint(f"For transaction_id { transaction_id } {action} Success. Message {message}")
                    return True,response,error_type
            except TimeoutException:
                pass

    except Exception as e:
        status = False
        message = f"For transaction_id { transaction_id } Error Occured => {str(e)}"
    return status, message, error_type
def create_user(driver,transaction_id,amount,username):
    status = False
    error = ''
    try:
        purchase_amount = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'Accounts_balance'))
        )
        purchase_amount.clear()
        purchase_amount.send_keys(amount)
        LogPrint(f"For # {transaction_id} Purchase Amount  Field Found and Data {amount} sent sucessfully.")

        username_field = driver.find_element(By.ID,'Accounts_comments')
        username_field.clear()
        username_field.send_keys(username)
        LogPrint(f"For # {transaction_id} Username Field Found and Data {username} sent sucessfully.")
        # driver.find_element(By.XPATH,'//*[@id="yw0"]/div/div[3]/input').click()
        # print("User Create sucessfuly")
        create_account_button = driver.find_element(By.CSS_SELECTOR,'input[type="submit"][name="yt0"][value="Create account"]')
        create_account_button.click()
        LogPrint(f"For # {transaction_id} Create account Button Clicked sucessfully")
        error_message_selector = ".alert.alert-error"
        success_message_selector = '.alert.alert-success'
        try:
            # Wait for the error message to appear
            message = WebDriverWait(driver, 10).until(
                        EC.any_of(
                            EC.presence_of_element_located((By.CSS_SELECTOR, error_message_selector)),
                            EC.presence_of_element_located((By.CSS_SELECTOR, success_message_selector)))
                    ).text
            if 'successfully created' in message:
                LogPrint(f"For # {transaction_id} User {username} Create sucessfully")
                return True, ''
            else:
                LogPrint(f"For # {transaction_id} User {username} Could not Create.")
                return False, message

        except:
            message = f"Reciept didn't Appear."
            return status,message


    except TimeoutException as e:
        status = False
        error = f"Timeout Exception: {str(e)}"
    except Exception as e:
        status = False
        error = str(e)

    return status, error

def main(data):
    transaction_id = ''
    finalStatus = False
    error_type = None
    finalMessage = ''
    date = datetime.now().strftime('%Y-%m-%d')
    driver = ''
    log_file_name = os.path.join(".","logs", f"Selenium-log-{date}.log")
    SetLogFile(log_file_name)
    try:
        driver = setup_driver()

        url = data["URL"]
        username = data["UserName"]
        passwd = data["Password"]
        player_username = data["player_username"]
        amount = data["amount"]
        action = data.get("action", "recharge")
        if 'create' in action:
            transaction_id = data.get("user_id")
        else:
            transaction_id = data.get("transaction_id")

        login_form_status, login_form_error = populate_username_passowrd_in_login_form(driver, transaction_id,url, username, passwd)
        if login_form_status is True:
            wait = WebDriverWait(driver, 60)
            # Define a condition to wait for page load (you can customize this)
            page_load_condition = EC.presence_of_element_located((By.ID, 'table-accounts'))
            # Wait until the page is fully loaded
            wait.until(page_load_condition)
            if 'create' in action:
                    finalStatus, finalMessage = create_user(driver,transaction_id,amount,player_username)
            else:
                search_status, search_error = perform_search(driver, transaction_id,player_username,action)
                if search_status is True:
                    finalStatus, finalMessage, error_type = perform_recharge_amount_actions(driver,transaction_id, action,amount)
                else:
                    finalMessage = search_error

        else:
            finalMessage = login_form_error

    except Exception as e:
        LogPrint(f"For transaction_id { transaction_id } Exception occurred: {e}")
        finalStatus = False
        finalMessage = str(e)
    finally:
        action = data.get("action", "recharge")
        if driver:
            uplaod_screenshot(driver, transaction_id, 'screenshot',action)
        else:
            finalMessage = "Selenium Driver Could not start."
        if 'create' in action:
            transaction_id = data.get('user_id')
        uplaod_screenshot(driver, transaction_id, 'screenshot',action)
        finalStatus = "success" if finalStatus is True else "failed"
        if 'create' in action:
            Send_Response(transaction_id, finalStatus, finalMessage, 'create-user')
        else:
            Send_Response(transaction_id, finalStatus, finalMessage,error_type=error_type)
        driver.quit()
        return finalStatus, finalMessage, error_type

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Process transaction data.')
    parser.add_argument('--transaction_id', type=int, default=123, help='Transaction ID')
    parser.add_argument('--user_id', type=int, default=123, help='Transaction ID')
    parser.add_argument('--URL', type=str, default='https://river-pay.com/office/login', help='URL')
    parser.add_argument('--UserName', type=str, default='copyandpen99', help='Username')
    parser.add_argument('--Password', type=str, default='copyandpen99', help='Password')
    parser.add_argument('--player_username', type=str, default='hassanlahore', help='Player username')
    parser.add_argument('--player_nickname', type=str, default='hassanlahore', help='Player nickname')
    parser.add_argument('--player_password', type=str, default='12345', help='Player password')
    parser.add_argument('--action', type=str, default='redeem', help='Action')
    parser.add_argument('--amount', type=str, default='10000', help='Amount')

    args = parser.parse_args()
    # Create a dictionary from command-line arguments
    data = {
        'transaction_id': args.transaction_id,
        'user_id': args.user_id,
        'URL': args.URL,
        'UserName': args.UserName,
        'Password': args.Password,
        'player_username': args.player_username,
        'player_nickname':args.player_nickname,
        'player_password':args.player_password,
        'action': args.action,
        'amount': args.amount
    }

    required_keys = list(data.keys())

    if not all(key in data for key in required_keys):
        LogPrint("Missing required keys in data dictionary")
        transaction_id = data.get('transaction_id', None)
        Send_Response(transaction_id=transaction_id, status="failed",
                      message="Missing required keys in data dictionary")
        exit()
    else:
        main(data)
