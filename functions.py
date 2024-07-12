import time
import requests
import yaml
import undetected_chromedriver as uc


def load_config():
    """
    This function will load the configuration file
    :return: config data
    """

    # Load configuration file
    with open('config.yml', 'r', encoding='UTF-8') as file:
        config = yaml.safe_load(file)

    return config


def uc_driver(config):
    """
    This function will create an undetected Chrome driver
    :return: undetected Chrome driver
    """

    # Create undetected Chrome driver
    driver = uc.Chrome(headless=True, use_subprocess=False, browser_executable_path=config['browser_executable_path'])

    return driver


def pass_captcha(config, country_code):
    """
    This function will use 2captcha to solve the Cloudflare Turnstile captcha
    :param config: configuration data
    :param country_code: request country code
    :return: Cloudflare Turnstile captcha token
    """

    # Set payload
    payload = {
        "key": config['2captcha_apikey'],
        "method": "turnstile",
        "sitekey": config['site_key'],
        "pageurl": config['basic_url'] + country_code + '/login',
        "json": 1
    }

    # Send request to 2captcha
    response = requests.post(url=config['twocaptcha_url'], data=payload)

    # Get response from 2captcha
    response_url = ("https://2captcha.com/res.php?key=" + config['2captcha_apikey'] + "&action=get&id=" +
                    response.json()['request'] + "&json=1")

    # Wait for response from 2captcha
    for i in range(0, 15):
        response = requests.get(url=response_url)
        if response.json()['request'] != "CAPCHA_NOT_READY":
            print("Captcha Solved")
            print("Cloudflare Turnstile Token: " + response.json().get('request'))
            break
        else:
            print("Captcha Not Ready")
        time.sleep(3)
    captcha_solution = response.json().get('request')

    return captcha_solution


def login(config, country_code, driver, token):
    """
    This function will login to the website
    :param config: configuration data
    :param country_code: request country code
    :param driver: undetected Chrome driver
    :param token: Cloudflare Turnstile captcha token
    :return: response data
    """

    # Open a blank page
    driver.get("about:blank")

    js_script = """
    function sendPostRequest(url, data, headers) {
        var xhr = new XMLHttpRequest();
        xhr.open("POST", url, true);
        for (var key in headers) {
            xhr.setRequestHeader(key, headers[key]);
        }
        xhr.onreadystatechange = function () {
            if (xhr.readyState === 4) {
                console.log("Response:", xhr.responseText);
                window.postMessage({status: xhr.status, response: xhr.responseText}, "*");
            }
        };
        xhr.send(data);
    }
    
    sendPostRequest(arguments[0], arguments[1], arguments[2]);
    """

    # Set target URL
    target_url = config['login_api_url']

    # Set payload
    payload = {
        "username": config['username'],
        "password": config['password'],
        "missioncode": country_code,
        "countrycode": "ind",
        "languageCode": "en-US",
        "captcha_version": "cloudflare-v1",
        "captcha_api_key": token
    }

    # Set headers
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Referer': config['referer_url'],
        'Route': 'ind/en/' + country_code,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/126.0.0.0 Safari/537.36',


    }
    payload_str = '&'.join([f'{key}={value}' for key, value in payload.items()])

    # Send request to login
    driver.execute_script(js_script, target_url, payload_str, headers)
    time.sleep(10)

    return driver.page_source


def appointment():
    pass
