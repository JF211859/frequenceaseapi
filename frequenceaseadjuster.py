import os
from random import getrandbits

import soundfile
import numpy as np
from flask import send_file, request, Blueprint
from scipy import fft



adjusterPage = Blueprint('adjuster', __name__, url_prefix = '/adjuster')

@adjusterPage.route("/hello_world")
def hello_world():
    return "Hello World!"

@adjusterPage.route("/return_file", methods=["GET"])
def return_file():

    if "file_name" not in request.args:
        print("file_name not defined")
        return "file_name not defined", 400

    return_file_name = request.args.get("file_name")

    return send_file(os.path.join("audio", return_file_name))

@adjusterPage.route("/", methods=['GET', 'POST'])
def adjuster():

    if 'file' in request.files:

        return_file_name = str(getrandbits(100)) + ".wav"

        return_file_path = os.path.join("audio", return_file_name)

        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            print('No selected file')
            return 'No file part', 400
        if file:
            filename = file.filename
            file.save(os.path.join('audio', filename))

            if "min_frequency" not in request.args or "max_frequency" not in request.args:
                print("frequencies not defined")
                return "frequencies not defined", 400

            min_frequency = int(request.args.get('min_frequency'))
            max_frequency = int(request.args.get('max_frequency'))
            desired_peak = int(((max_frequency - min_frequency) / 2) + min_frequency)

            audio_samples, sample_rate = soundfile.read(os.path.join('audio', filename), dtype="int16")

            fft_to_hz = sample_rate / len(audio_samples)

            fft_data = fft.rfft(audio_samples)

            current_peak = np.argmax(fft_data) * fft_to_hz
            shift = int((current_peak - desired_peak) / fft_to_hz)

            if shift > 0:

                fft_data = fft_data[shift:]
                fft_data = np.concatenate([fft_data, ([0] * shift)])

            else:

                shift *= -1

                fft_data = fft_data[:-shift]
                fft_data = np.concatenate([([0] * shift), fft_data])

            shifted_audio = fft.irfft(fft_data)
            shifted_audio = np.array([sample.real for sample in shifted_audio]) # pylint: disable=no-member

            shifted_audio /= max(shifted_audio)

            soundfile.write(return_file_path, shifted_audio, sample_rate)

            return request.url_root + "/adjuster/return_file?file_name=" + return_file_name, 200

    else:
        return '''
            <!doctype html>
            <title>Upload new File</title>
            <h1>Upload new File</h1>
            <form method=post enctype=multipart/form-data>
            <input type=file name=file>
            <input type=submit value=Upload>
            </form>
        ''', 200