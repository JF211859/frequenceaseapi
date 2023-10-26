from flask import Flask

app = Flask(__name__)

from frequenceaseadjuster import adjusterPage
from frequenceasetester import testerPage

app.register_blueprint(testerPage)
app.register_blueprint(adjusterPage)