import os

import soundfile

from flask import Flask, send_file, request
import werkzeug


app = Flask(__name__)



@app.route("/hello_world")
def hello_world():
    return "Hello World!"

@app.route("/cantina", methods=['GET'])
def cantina():
    scale = float(request.args.get('scale'))
    audio_samples, sample_rate = soundfile.read("audio/CantinaBand3.wav", dtype="int16")
    soundfile.write('audio/return.wav', audio_samples, int(sample_rate * scale))
    return send_file("audio/return.wav")

@app.route("/postfile", methods=['GET', 'POST'])
def postfile():
    if request.method == "POST":
        if 'file' not in request.files:
            print('No file part')
            return 'No file part', 400
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            print('No selected file')
            return 'No file part', 400
        if file:
            filename = werkzeug.secure_filename(file.filename)
            file.save(os.path.join('audio', filename))
            return 200
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=text name=filename>
      <input type=submit value=Upload>
    </form>
    '''


