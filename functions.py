import time
import yaml
import pyautogui
import pyscreeze
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
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
    :return: None
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
        try:
            captcha = pyscreeze.locateOnScreen(config['captcha_path'], confidence=0.9, grayscale=True)
            if captcha is not None:
                break
        except pyscreeze.ImageNotFoundException:
            pass
    location = pyscreeze.locateOnScreen(config['captcha_click_path'], confidence=0.8)
    center = pyautogui.center(location)
    time.sleep(2)
    pyautogui.click(center)
    time.sleep(10)

    # Enter the username and password
    windows = driver.window_handles
    driver.switch_to.window(windows[-1])
    driver.find_element(By.XPATH, config['username_xpath']).send_keys(config['username'])
    driver.find_element(By.XPATH, config['password_xpath']).send_keys(config['password'])
    driver.find_element(By.XPATH, config['submit_xpath']).click()


def appointment(config, driver, country_code):
    pass
