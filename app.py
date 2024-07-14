from flask import Flask, render_template, request, jsonify
import functions

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/v1/', methods=['POST'])
def api_v1():
    data = request.get_json()
    config = functions.load_config()
    country_code = data['VisaDestinationLocations']['countryName']
    application_center = data['AppointmentLocations']['cityName']
    driver = functions.uc_driver(config)
    is_login_success = functions.login(config, driver, country_code)
    if is_login_success:
        return functions.appointment(config, driver, application_center)
    else:
        return functions.login_error()


if __name__ == '__main__':
    app.run()
