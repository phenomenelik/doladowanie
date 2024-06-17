import os
import time
from pathlib import Path

from selenium import webdriver
from dotenv import load_dotenv
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, WebDriverException


debugging = True
load_dotenv()

PHONE_NUMBER = os.getenv("PHONE_NUMBER")
EMAIL = os.getenv("EMAIL")
FIRST_NAME = os.getenv("FIRST_NAME")
LAST_NAME = os.getenv("LAST_NAME")
CARD_NUM = os.getenv("CARD_NUM")
CARD_MONTH = os.getenv("CARD_MONTH")
CARD_YEAR = os.getenv("CARD_YEAR")
CARD_CVV = os.getenv("CARD_CVV")
TOP_UP = os.getenv("TOP_UP")


script_directory = Path(__file__).resolve().parent
driver_path = script_directory.joinpath("driver", "chromedriver")
chrome_options = Options()
if debugging:
    chrome_options.add_experimental_option("detach", True)
else:
    chrome_options.add_argument("--headless")


def set_field_to_password(driver, element_id):
    driver.execute_script(f"document.getElementById('{element_id}').type = 'password'")


def wait_for_element(driver, by, element_identifier, timeout=10):
    try:
        element_present = EC.presence_of_element_located((by, element_identifier))
        WebDriverWait(driver, timeout).until(element_present)
    except TimeoutException:
        print(f"Timed out waiting for {element_identifier}")
        return None
    return driver.find_element(by, element_identifier)


def enter_phone_and_email(driver):
    driver.get("https://doladowania.t-mobile.pl/doladowanie")

    accept_cookies_button = wait_for_element(driver, By.XPATH, "//button[text()[normalize-space()='Akceptuj wszystkie']]")
    phone_number_input = wait_for_element(driver, By.ID, "form-phone-0")
    email_input = wait_for_element(driver, By.ID, "form-email")
    next_step_button = wait_for_element(driver, By.ID, "submit-step-1")

    if accept_cookies_button and phone_number_input and email_input:
        set_field_to_password(driver, "form-phone-0")
        set_field_to_password(driver, "form-email")

        accept_cookies_button.click()
        phone_number_input.send_keys(PHONE_NUMBER)
        email_input.send_keys(EMAIL)

    time.sleep(4) # todo dodac legit waitera
    next_step_button.click()


def choose_top_up_amount(driver):
    next_step_button = wait_for_element(driver, By.ID, "submit-step-2")
    top_up_button = wait_for_element(driver, By.XPATH, f"//li[@class='topup-amount topup-{TOP_UP}']")
    top_up_button.click()
    time.sleep(1.5)
    next_step_button.click()


def check_required_consents(driver):
    terms_and_conditions_checkbox = wait_for_element(driver, By.XPATH, "(//span[@class='check-label-box'])[3]")
    service_agreement_checkbox = wait_for_element(driver, By.XPATH, "//label[@for='payment']//span")
    service_agreement_checkbox = wait_for_element(driver, By.XPATH, "//label[@for='payment']//span")
    submit_button = wait_for_element(driver, By.ID, "submit-step-3")

    terms_and_conditions_checkbox.click()
    service_agreement_checkbox.click()
    submit_button.click()


def payment_form(driver):
    pay_by_card_radiobutton = wait_for_element(driver, By.ID, "payway-radio-CARD")
    pay_by_card_radiobutton.click()
    driver.switch_to.frame(driver.find_element(By.ID, 'iframeCards'))
    card_number_input = wait_for_element(driver, By.ID, "cardNumber")
    first_name_input = wait_for_element(driver, By.ID, "firstName")
    last_name_input = wait_for_element(driver, By.ID, "lastName")
    expiration_date_input = wait_for_element(driver, By.ID, "expirationDate")
    cvv_input = wait_for_element(driver, By.ID, "code")

    # todo ładniej ograć
    set_field_to_password(driver, "cardNumber")
    set_field_to_password(driver, "firstName")
    set_field_to_password(driver, "lastName")
    set_field_to_password(driver, "expirationDate")
    set_field_to_password(driver, "code")
    card_number_input.send_keys(CARD_NUM)
    first_name_input.send_keys(FIRST_NAME)
    last_name_input.send_keys(LAST_NAME)
    expiration_date_input.send_keys(CARD_MONTH + CARD_YEAR)
    cvv_input.send_keys(CARD_CVV)
    driver.switch_to.default_content()
    pay_button = wait_for_element(driver, By.XPATH, "//span[text()='Płacę']")
    pay_button.click()


def payment_confirmation(driver):
    pass


def main():
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        enter_phone_and_email(driver)
        choose_top_up_amount(driver)
        check_required_consents(driver)
        payment_form(driver)
    except WebDriverException as e:
        print(f"General webdriver error {e}")
    finally:
        if not debugging:
            driver.quit()


if __name__ == "__main__":
    main()
 