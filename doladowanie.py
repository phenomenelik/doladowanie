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
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException

debugging = True
load_dotenv()

PHONE_NUMBER = os.getenv("PHONE_NUMBER")
EMAIL = os.getenv("EMAIL")
CARD_NUM = os.getenv("CARD_NUM")
CARD_MONTH = os.getenv("CARD_MONTH")
CARD_YEAR = os.getenv("CARD_YEAR")
CARD_CVV = os.getenv("CARD_CVV")
PREPAID = 30


script_directory = Path(__file__).resolve().parent
driver_path = script_directory.joinpath("driver", "chromedriver")
chrome_options = Options()
if debugging:
    chrome_options.add_experimental_option("detach", True)
else:
    chrome_options.add_argument("--headless")


def set_field_to_password(driver, element_id):
    driver.execute_script(f"document.getElementById('{element_id}').type = 'password'")


def wait_for_element(driver, by, element_identifier, timeout=5):
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

    time.sleep(1)
    next_step_button.click()


def main():
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        enter_phone_and_email(driver)
    except WebDriverException as e:
        print(f"General webdriver error {e}")
    finally:
        if not debugging:
            driver.quit()


if __name__ == "__main__":
    main()
