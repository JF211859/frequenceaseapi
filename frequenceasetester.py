import os

import soundfile

from flask import Flask, send_file, request, Blueprint
import werkzeug

from flask import Flask

testerPage = Blueprint('tester', __name__, url_prefix = '/tester')
@testerPage.route('/hello_world')
def hello_world():
    return "Hello Tester!"
