import os
from pathlib import Path
from selenium import webdriver
from dotenv import load_dotenv
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException
from seleniumactions import Actions, FluentFinder, Locator, Using, LocatorExists


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

card_data = ["firstName", "lastName", "cardNumber", "expirationDate", "code"]

script_directory = Path(__file__).resolve().parent
driver_path = script_directory.joinpath("driver", "chromedriver")
chrome_options = Options()
if debugging:
    chrome_options.add_experimental_option("detach", True)
else:
    chrome_options.add_argument("--headless")

service = Service(driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

timeouts = {
    "short": 2,
    "medium": 3,
    "long": 5,
    "absurd": 10
}
finder = FluentFinder(
    driver,
    timeouts=timeouts,
    default_timeout=timeouts["medium"]
)
actions = Actions(
    finder,
    wait_for_condition_timeout=15,
    wait_between=0.5
)


def set_field_to_password(element_id):
    driver.execute_script(f"document.getElementById('{element_id}').type = 'password'")


def set_fields_to_password(list_of_element_ids):
    for element_id in list_of_element_ids:
        set_field_to_password(element_id)


def switch_to_iframe(frame_id):
    iframe_driver = driver.find_element(Using.ID, frame_id)
    driver.switch_to.frame(iframe_driver)


def switch_to_default_content():
    driver.switch_to.default_content()


def open_website():
    actions.goto("https://doladowania.t-mobile.pl/doladowanie")


def enter_phone_and_email():
    accept_cookies_button = Locator(Using.XPATH, "//button[text()[normalize-space()='Akceptuj wszystkie']]").get_by()
    phone_number_input = Locator(Using.ID, "form-phone-0").get_by()
    email_input = Locator(Using.ID, "form-email").get_by()

    actions.click(accept_cookies_button)
    actions.type_text(phone_number_input, PHONE_NUMBER)
    actions.type_text(email_input, EMAIL)
    actions.sleep(2)  # loader nr telefonu
    next_step_button = Locator(Using.ID, "submit-step-1").get_by()
    actions.submit(next_step_button)


def choose_top_up_amount():
    top_up_button = Locator(Using.XPATH, "//li[@class='topup-amount topup-{TOP_UP}']")
    actions.click(top_up_button.get_by(TOP_UP=TOP_UP))

    next_step_button = Locator(Using.ID, "submit-step-2").get_by()
    actions.submit(next_step_button)


def check_required_consents():
    terms_and_conditions_checkbox = Locator(Using.XPATH, "(//span[@class='check-label-box'])[3]").get_by()
    service_agreement_checkbox = Locator(Using.XPATH, "//label[@for='payment']//span").get_by()
    submit_button = Locator(Using.ID, "submit-step-3").get_by()

    actions.click(terms_and_conditions_checkbox)
    actions.click(service_agreement_checkbox)
    actions.submit(submit_button)


def payment_form():
    pay_by_card_radiobutton = Locator(Using.ID, "payway-radio-CARD").get_by()
    actions.wait_for(LocatorExists(pay_by_card_radiobutton), timeout="long")
    actions.click(pay_by_card_radiobutton)

    switch_to_iframe("iframeCards")

    card_number_input = Locator(Using.ID, "cardNumber").get_by()
    first_name_input = Locator(Using.ID, "firstName").get_by()
    last_name_input = Locator(Using.ID, "lastName").get_by()
    expiration_date_input = Locator(Using.ID, "expirationDate").get_by()
    cvv_input = Locator(Using.ID, "code").get_by()

    set_fields_to_password(card_data)
    actions.type_text(card_number_input, CARD_NUM)
    actions.type_text(first_name_input, FIRST_NAME)
    actions.type_text(last_name_input, LAST_NAME)
    actions.type_text(expiration_date_input, CARD_MONTH + CARD_YEAR)
    actions.type_text(cvv_input, CARD_CVV)

    switch_to_default_content()

    pay_button = Locator(Using.XPATH, "//span[text()='Płacę']").get_by()
    actions.click(pay_button)


def payment_confirmation():
    root_element = Locator(Using.ID, "root").get_by()
    condition = LocatorExists(root_element)
    actions.wait_for(condition, timeout="long")


def send_message():
    pass


def main():

    try:
        open_website()
        enter_phone_and_email()
        choose_top_up_amount()
        check_required_consents()
        payment_form()
        payment_confirmation()
    except WebDriverException as e:
        print(f"General webdriver error {e}")
    finally:
        if not debugging:
            driver.quit()


if __name__ == "__main__":
    main()
