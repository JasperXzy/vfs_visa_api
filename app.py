from flask import Flask, render_template, request, jsonify
import functions

app = Flask(__name__)


@app.route('/')
def index():  # put application's code here
    return render_template('index.html')


@app.route('/api/v1/', methods=['POST'])
def api_v1():
    data = request.get_json()
    country_code = data['countryCode']
    return functions.pass_captcha(country_code)


if __name__ == '__main__':
    app.run()
