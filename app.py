from flask import Flask, render_template, request, jsonify
import functions

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/v1/', methods=['POST'])
def api_v1():
    """
    This function will handle POST requests
    :return: Response json file
    """

    # Load POST request data
    data = request.get_json()

    # Load configuration data
    basic_config = functions.load_config('./config.yml')

    # Load country code configuration data
    country_code_config = functions.load_config('./dicts/des_country_code.yml')
    country_name = data['VisaDestinationLocations']['countryName']
    country_code = country_code_config[country_name]

    # Load country configuration data
    appointment_config = functions.load_config(f'./dicts/{country_code}.yml')

    # Merge basic configuration and country configuration
    config = {**basic_config, **appointment_config}

    # Select application center
    application_center = data['AppointmentLocations']['cityName']
    application_center_name = config[application_center]

    # Start the driver
    driver = functions.uc_driver(config)

    # Judge whether the login is successful
    is_login_success = functions.login(config, driver, country_code)

    # If login is successful, then go to the appointment page
    if is_login_success:
        return functions.appointment(config, driver, application_center_name)
    else:
        return functions.login_error()


if __name__ == '__main__':
    app.run()
