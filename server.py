import config
import logging
from datetime import datetime
from whisper_cpp_python import Whisper
from flask import Flask, request, send_file, jsonify, render_template


app = Flask(__name__)
__whisper__ = None
__chatglm__ = None

PROMPT_TPL = '{prompt}'


def get_llm():
    global __chatglm__
    if __chatglm__ is None:
        try:
            import chatglm_cpp
            __chatglm__ = chatglm_cpp.Pipeline(config.LLM_MODEL_PATH)
        except Exception:
            pass
    return __chatglm__


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


@app.route('/speech_translate', methods=['POST'])
def speech_to_text_translate():
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


@app.route('/speech_transcribe', methods=['POST'])
def speech_to_text_transcribe():
    wav_file = request.files.get('file', None)
    if wav_file is None:
        return 'Require file parameter', 400
    try:
        whisper = get_whisper_engine()
        resp = whisper.transcribe(wav_file, language='auto')
        return jsonify(resp)
    except Exception as e:
        logging.exception(e)
        return 'Server Error', 500


@app.route('/chat')
def chat():
    return render_template('chat.html')


@app.route('/chat_msg', methods=['POST'])
def chat_msg():
    data = request.json
    prompt = data['prompt']
    prompt_tpl = data.get('prompt_template', PROMPT_TPL)
    resp = generate_chat_response(prompt, prompt_tpl)
    return jsonify({'text': resp})


def apply_template(prompt, prompt_tpl):
    if '{prompt}' in prompt_tpl:
        return prompt_tpl.replace('{prompt}', prompt)
    return prompt_tpl + prompt


def generate_chat_response(prompt, prompt_tpl):
    try:
        import chatglm_cpp
    except Exception:
        return 'Cannot Load ChatGLM'

    prompt = apply_template(prompt, prompt_tpl)

    llm = get_llm()
    params = {
        'max_length': 4096,
        'max_context_length': 2048,
        'do_sample': True,
        'top_k': 0,
        'top_p': 0.7,
        'temperature': 0.95,
        'repetition_penalty': 1.0,
        'stream': True,
    }
    msgs = [
        chatglm_cpp.ChatMessage('user', prompt)
    ]
    output = ''
    first = True
    for chunk in llm.chat(msgs, **params):
        if first and '\n' in chunk.content:
            first = False
            output += chunk.content.removeprefix('\n')
        else:
            output += chunk.content
    return output


def start_server(host='127.0.0.1', port=7890, debug=True):
    app.run(host=host, port=port, debug=debug)
