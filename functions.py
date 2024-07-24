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


def load_config(config_path):
    """
    This function will load the configuration file
    :return: Configuration data
    """

    # Load configuration file
    with open(config_path, 'r', encoding='UTF-8') as file:
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
    wait.until(EC.presence_of_element_located((By.XPATH, config['make_appointment_xpath'])))
    driver.find_element(By.XPATH, config['make_appointment_xpath']).click()

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
    :return: Login failed message
    """
    print("Login Failed")

    return "Login Failed"


def appointment(config, driver, application_center):
    """
    This function will book an appointment
    :param config: Configuration data
    :param driver: undetected Chrome driver
    :param application_center: Application center
    :return: Page text
    """

    # Create a wait object
    wait = WebDriverWait(driver=driver, timeout=20, poll_frequency=0.5)

    # Load the appointment URL
    time.sleep(2)
    wait.until(EC.presence_of_element_located((By.XPATH, config['new_booking_xpath'])))
    driver.find_element(By.XPATH, config['new_booking_xpath']).click()

    # Select application center
    time.sleep(2)
    try:
        wait.until(EC.element_to_be_clickable((By.XPATH, config['application_center_xpath'])))
        driver.find_element(By.XPATH, config['application_center_xpath']).click()
        wait.until(EC.element_located_to_be_selected((By.XPATH, config['application_center_select_xpath'])))
        application_center_select = driver.find_element(By.XPATH, config['application_center_select_xpath'])
        Select(application_center_select).select_by_visible_text(application_center)
    except Exception as e:
        print(e)

    # Select appointment category
    time.sleep(2)
    try:
        wait.until(EC.element_to_be_clickable((By.XPATH, config['appointment_category_xpath'])))
        driver.find_element(By.XPATH, config['appointment_category_xpath']).click()
        wait.until(EC.element_located_to_be_selected((By.XPATH, config['appointment_category_select_xpath'])))
        appointment_category_select = driver.find_element(By.XPATH, config['appointment_category_select_xpath'])
        Select(appointment_category_select).select_by_visible_text("Short Term")
    except Exception as e:
        print(e)

    # Select sub category
    time.sleep(2)
    try:
        wait.until(EC.element_to_be_clickable((By.XPATH, config['appointment_sub_category_xpath'])))
        driver.find_element(By.XPATH, config['appointment_sub_category_xpath']).click()
        wait.until(EC.element_located_to_be_selected((By.XPATH, config['appointment_sub_category_select_xpath'])))
        appointment_sub_category_select = driver.find_element(By.XPATH, config['appointment_sub_category_select_xpath'])
        Select(appointment_sub_category_select).select_by_visible_text("Tourism")
    except Exception as e:
        print(e)
    time.sleep(5)

    return driver.text


if __name__ == '__main__':
    # Load POST request data
    data = json.load(open('./test/test_post.json', 'r', encoding='utf-8'))

    # Load configuration data
    basic_config = load_config('./config.yml')

    # Load country code configuration data
    country_code_config = load_config('./dicts/des_country_code.yml')
    country_name = data['VisaDestinationLocations']['countryName']
    country_code = country_code_config[country_name]

    # Load country configuration data
    appointment_config = load_config(f'./dicts/{country_code}.yml')

    # Merge basic configuration and country configuration
    config = {**basic_config, **appointment_config}

    # Select application center
    application_center = data['AppointmentLocations']['cityName']
    application_center_name = config[application_center]

    # Start the driver
    driver = uc_driver(config)

    # Judge whether the login is successful
    is_login_success = login(config, driver, country_code)

    # If login is successful, then go to the appointment page
    if is_login_success:
        appointment(config, driver, application_center_name)
    else:
        login_error()
