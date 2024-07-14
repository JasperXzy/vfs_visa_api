import time
import json
import yaml
import pyautogui
import pyscreeze
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC


def load_config():
    """
    This function will load the configuration file
    :return: Configuration data
    """

    # Load configuration file
    with open('config.yml', 'r', encoding='UTF-8') as file:
        config = yaml.safe_load(file)

    return config


def uc_driver(config):
    """
    This function will create an undetected Chrome driver
    :param config: Configuration data
    :return: undetected Chrome driver
    """

    # Create custom undetected Chrome driver
    options = uc.ChromeOptions()
    driver = uc.Chrome(options=options, headless=False, use_subprocess=False,
                       driver_executable_path=config['browser_driver_path'])
    driver.maximize_window()

    return driver


def login(config, driver, country_code):
    """
    This function will login to the website
    :param config: Configuration data
    :param driver: undetected Chrome driver
    :param country_code: Requested country code
    :return: True if login is successful, False is failed
    """

    # Create a wait object
    wait = WebDriverWait(driver=driver, timeout=20, poll_frequency=0.5)

    # Load the login URL
    login_url = config['basic_url'] + country_code + "/book-an-appointment"
    driver.get(login_url)

    # Wait for booking the page to load
    appointment_xpath = "//*[@id=\"__layout\"]/div/main/div/div/div[3]/div/p[29]/a"
    wait.until(EC.presence_of_element_located((By.XPATH, appointment_xpath)))
    driver.find_element(By.XPATH, appointment_xpath).click()

    # Wait for the solution of Cloudflare Turnstile
    while True:
        time.sleep(5)
        try:
            captcha = pyscreeze.locateOnScreen(config['captcha_path'], confidence=0.8, grayscale=True)
            captcha_success = pyscreeze.locateOnScreen(config['captcha_success_path'], confidence=0.8, grayscale=True)
            if captcha or captcha_success is not None:
                break
            else:
                continue
        except pyscreeze.ImageNotFoundException:
            print("Image not found")
            continue
    location = pyscreeze.locateOnScreen(config['captcha_click_path'], confidence=0.8)
    center = pyautogui.center(location)
    time.sleep(2)
    pyautogui.click(center)
    time.sleep(3)

    # Enter the username and password
    windows = driver.window_handles
    driver.switch_to.window(windows[-1])
    time.sleep(1)
    driver.find_element(By.XPATH, config['username_xpath']).send_keys(config['username'])
    time.sleep(1)
    driver.find_element(By.XPATH, config['password_xpath']).send_keys(config['password'])
    time.sleep(1)
    driver.find_element(By.XPATH, config['submit_xpath']).click()

    try:
        if wait.until(EC.presence_of_element_located((By.XPATH, config['new_booking_xpath']))) is not None:
            time.sleep(2)
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False


def login_error():
    """
    This function will handle login errors
    :return: None
    """
    print("Login Failed")


def appointment(config, driver, application_center):
    """
    This function will book an appointment
    :param config: Configuration data
    :param driver: undetected Chrome driver
    :param application_center: Application center
    :return:
    """

    # Create a wait object
    wait = WebDriverWait(driver=driver, timeout=20, poll_frequency=0.5)

    # Load the appointment URL
    wait.until(EC.element_to_be_clickable((By.XPATH, config['new_booking_xpath'])))
    driver.find_element(By.XPATH, config['new_booking_xpath']).click()

    # Select application center
    wait.until(EC.presence_of_element_located((By.XPATH, config['application_center_xpath'])))
    driver.find_element(By.XPATH, config['application_center_xpath']).click()
    wait.until(EC.element_located_to_be_selected((By.XPATH, config['application_center_select_xpath'])))
    application_center_select = driver.find_element(By.XPATH, config['application_center_select_xpath'])
    Select(application_center_select).select_by_visible_text(application_center)

    # Select appointment category
    wait.until(EC.presence_of_element_located((By.XPATH, config['appointment_category_xpath'])))
    driver.find_element(By.XPATH, config['appointment_category_xpath']).click()
    wait.until(EC.element_located_to_be_selected((By.XPATH, config['appointment_category_select_xpath'])))
    appointment_category_select = driver.find_element(By.XPATH, config['appointment_category_select_xpath'])
    Select(appointment_category_select).select_by_visible_text("Short Term")

    # Select sub category
    wait.until(EC.presence_of_element_located((By.XPATH, config['appointment_sub_category_xpath'])))
    driver.find_element(By.XPATH, config['appointment_sub_category_xpath']).click()
    wait.until(EC.element_located_to_be_selected((By.XPATH, config['appointment_sub_category_select_xpath'])))
    appointment_sub_category_select = driver.find_element(By.XPATH, config['appointment_sub_category_select_xpath'])
    Select(appointment_sub_category_select).select_by_visible_text("Tourism")

    time.sleep(5)

    return driver.text


if __name__ == '__main__':
    test_data = json.load(open('./test/test_post.json', 'r', encoding='utf-8'))
    test_config = load_config()
    test_country_code = test_data['VisaDestinationLocations']['countryName']
    test_application_center = test_data['AppointmentLocations']['cityName']
    test_driver = uc_driver(test_config)
    is_login_success = login(test_config, test_driver, test_country_code)
    if is_login_success:
        appointment(test_config, test_driver, test_application_center)
    else:
        login_error()
