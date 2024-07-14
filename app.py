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
    driver = functions.uc_driver(config)
    return functions.login(config, driver, country_code)


if __name__ == '__main__':
    app.run()
