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
    country_code = data['countryCode']
    token = functions.pass_captcha(config, country_code)
    driver = functions.uc_driver(config)
    return functions.login(config, country_code, driver, token)


if __name__ == '__main__':
    app.run()
