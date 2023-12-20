import config
import logging
from datetime import datetime
from whisper_cpp_python import Whisper
from flask import Flask, request, send_file, jsonify, render_template


app = Flask(__name__)
__whisper__ = None


def get_whisper_engine():
    global __whisper__
    if __whisper__ is None:
        model = config.WHISPER_MODEL_PATH
        __whisper__ = Whisper(model_path=model, n_threads=4)
        __whisper__.params.language = 'zh'.encode('utf-8')
    return __whisper__


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/speech', methods=['POST'])
def speech_to_text():
    wav_file = request.files.get('file', None)
    if wav_file is None:
        return 'Require file parameter', 400
    try:
        whisper = get_whisper_engine()
        resp = whisper.translate(wav_file, 'translate into English')
        return jsonify(resp)
    except Exception as e:
        logging.exception(e)
        return 'Server Error', 500


def start_server(host='127.0.0.1', port=7890, debug=True):
    app.run(host=host, port=port, debug=debug)
