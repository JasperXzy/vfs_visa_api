import time
import requests
import yaml


def pass_captcha(country_code):
    """
    This function will use 2captcha to solve the Cloudflare Turnstile Captcha
    :param country_code: request country code
    :return: Cloudflare Turnstile Captcha Token
    """

    # Load config file
    with open('./config.yml', 'r') as file:
        config = yaml.safe_load(file)

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
            break
        else:
            print("Captcha Not Ready")
        time.sleep(5)

    captcha_solution = response.json().get('request')

    return captcha_solution


def login(country_code, captcha_token):
    pass


def appointment(country_code, application_center):
    pass

