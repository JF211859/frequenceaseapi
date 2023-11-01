import os

import soundfile

from flask import Flask, send_file, request, Blueprint
import werkzeug

from flask import Flask

from scipy import signal, fft

import numpy as np

from pydub import AudioSegment

from time import sleep

adjusterPage = Blueprint('adjuster', __name__, url_prefix = '/adjuster')

@adjusterPage.route("/hello_world")
def hello_world():
    return "Hello World!"

@adjusterPage.route("/", methods=['GET', 'POST'])
def adjuster():
    return_file_name = os.path.join("audio", "return.wav")

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
            filename = file.filename
            file.save(os.path.join('audio', filename))
            shift = int(request.args.get('shift'))
            audio_samples, sample_rate = soundfile.read(os.path.join('audio', filename), dtype="int16")

            fft_data = fft.fft(audio_samples)

            halfway_point = int(len(fft_data) / 2)
            positive_fft_data = fft_data[:halfway_point]
            negative_fft_data = fft_data[halfway_point:]

            if shift > 0:

                positive_fft_data = positive_fft_data[shift:]
                positive_fft_data = np.concatenate([positive_fft_data, ([0] * shift)])

                negative_fft_data = negative_fft_data[:-shift]
                negative_fft_data = np.concatenate([([0] * shift), negative_fft_data])

            else:

                shift *= -1

                positive_fft_data = positive_fft_data[:-shift]
                positive_fft_data = np.concatenate([([0] * shift), positive_fft_data])

                negative_fft_data = negative_fft_data[shift:]
                negative_fft_data = np.concatenate([negative_fft_data, ([0] * shift)])


            new_fft_data = np.concatenate([positive_fft_data, negative_fft_data])

            shifted_audio = fft.ifft(new_fft_data)
            shifted_audio = np.array([sample.real for sample in shifted_audio])

            shifted_audio = shifted_audio.astype(np.short)

            audio_segment = AudioSegment(
                shifted_audio.tobytes(),
                frame_rate=sample_rate,
                sample_width=shifted_audio.dtype.itemsize,
                channels=1
            )

            beginning = audio_segment[:len(audio_segment) / 3]
            middle = audio_segment[len(audio_segment) / 3:len(audio_segment) * 2 / 3]
            end = audio_segment[len(audio_segment) * 2 / 3:]

            middle = middle + 15
            audio_segment = beginning + middle + end

            audio_segment.export(return_file_name, format="wav")

            sleep(1)

            print(f"sending {return_file_name}")

            return send_file(return_file_name)

    if request.method == "GET":
        if os.path.exists(return_file_name):
            file_handle = open(return_file_name, 'rb')
            try:
                os.remove(return_file_name)
            except Exception as error:
                print("Error removing or closing downloaded file handle", error)
            return send_file(file_handle, mimetype="wav")


        else:

            return '''
            <!doctype html>
            <title>Upload new File</title>
            <h1>Upload new File</h1>
            <form method=post enctype=multipart/form-data>
            <input type=file name=file>
            <input type=submit value=Upload>
            </form>
            '''

@adjusterPage.route("/postfile", methods=['GET', 'POST'])
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
            filename = file.filename
            file.save(os.path.join('audio', filename))
            return "File Uploaded", 200
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''


