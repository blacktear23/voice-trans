import json
import config
import logging
import requests
from datetime import datetime
from whisper_cpp_python import Whisper
from flask import Flask, request, send_file, jsonify, render_template, redirect
from prompt_templates import PROMPT_TPLS
from whisper_api import WhisperAPI


app = Flask(__name__)
__whisper__ = None
__chatglm__ = None
__whisper_api__ = None

PROMPT_TPL = '{prompt}'
MAX_CHAT_HISTORY = 9
WHISPER_API_HOST = '101.36.226.223'
WHISPER_API_PORT = 8888


def get_llm():
    global __chatglm__
    if __chatglm__ is None:
        try:
            import chatglm_cpp
            __chatglm__ = chatglm_cpp.Pipeline(config.LLM_MODEL_PATH)
        except Exception:
            pass
    return __chatglm__


def get_whisper_engine(language=None):
    global __whisper__
    if __whisper__ is None:
        model = config.WHISPER_MODEL_PATH
        __whisper__ = Whisper(model_path=model, n_threads=4)
        __whisper__.params.language = 'auto'.encode('utf-8')
    if language is not None:
        __whisper__.params.language = language.encode('utf-8')
    return __whisper__


def get_whisper_api():
    global __whisper_api__
    if __whisper_api__ is None:
        __whisper_api__ = WhisperAPI(WHISPER_API_HOST, WHISPER_API_PORT)
    return __whisper_api__


@app.route('/')
def index():
    return redirect('/chat')


@app.route('/translate')
def translate():
    return render_template('translate.html')


@app.route('/speech_translate', methods=['POST'])
def speech_to_text_translate():
    wav_file = request.files.get('file', None)
    if wav_file is None:
        return 'Require file parameter', 400
    language = request.form.get('language', 'auto')
    print(language)
    print(request.form)
    try:
        whisper = get_whisper_api()
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
        whisper = get_whisper_api()
        resp = whisper.transcribe(wav_file, lang='auto')
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


@app.route('/chat_msgs', methods=['POST'])
def chat_msgs():
    data = request.json
    prompts = data.get('prompts', [])
    prompt_tpl = data.get('prompt_template', PROMPT_TPL)
    num_histories = 1
    try:
        num_histories = int(data.get('num_history', 1))
        num_histories = min(num_histories, MAX_CHAT_HISTORY)
    except Exception:
        pass
    resp = generate_chat_response_by_messages(prompts, prompt_tpl, num_histories)
    return jsonify({'text': resp})


@app.route('/prompt_templates')
def prompt_tpls():
    return jsonify(PROMPT_TPLS)


def apply_template(prompt, prompt_tpl):
    if '{search_ctx}' in prompt_tpl:
        search_result = request_search_result(prompt)
        if '{prompt}' in prompt_tpl:
            return prompt_tpl.format(search_ctx=search_result, prompt=prompt)
        else:
            return prompt_tpl.format(search_ctx=search_result) + prompt
    if '{prompt}' in prompt_tpl:
        return prompt_tpl.replace('{prompt}', prompt)
    return prompt_tpl + prompt


def request_search_result(query):
    if not config.ENABLE_SEARCH:
        return 'Nothing'
    resp = requests.post(config.SEARCH_API, data=json.dumps({'query': query}), headers={'Content-Type': 'application/json'})
    rjson = resp.json()
    ret = []
    idx = 0
    for i in rjson[0:3]:
        idx += 1
        title = i.get('title', '')
        desc = i.get('desc', '')
        item = f'{idx}. Title: {title}\n{desc}'
        ret.append(item)
    return '\n'.join(ret)


def generate_chat_response_by_messages(prompts, prompt_tpl, num_histories):
    try:
        import chatglm_cpp
    except Exception:
        return 'Cannot Load ChatGLM'

    msgs = process_prompts(prompts, prompt_tpl, num_histories)
    if len(msgs) == 0:
        return ''

    print(msgs)
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
    output = ''
    first = True
    for chunk in llm.chat(msgs, **params):
        if first and '\n' in chunk.content:
            first = False
            output += chunk.content.removeprefix('\n')
        else:
            output += chunk.content
    return output


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


def process_prompts(prompts, prompt_tpl, num_histories):
    import chatglm_cpp
    ret = []
    if len(prompts) == 0:
        return ret

    last_prompt = prompts[-1]
    if last_prompt.get('role') != 'user':
        return ret

    last_content = apply_template(last_prompt.get('content'), prompt_tpl)
    for prompt in prompts[:-1]:
        role = prompt.get('role')
        item = None
        if role == 'user':
            item = chatglm_cpp.ChatMessage('user', prompt.get('content', ''))
        elif role == 'assistant':
            item = chatglm_cpp.ChatMessage('assistant', prompt.get('content', ''))

        if item is not None:
            ret.append(item)

    ret.append(chatglm_cpp.ChatMessage('user', last_content))
    if len(ret) > num_histories:
        spos = len(ret) - num_histories
        return ret[spos:]
    return ret


def start_server(host='127.0.0.1', port=7890, debug=True):
    app.run(host=host, port=port, debug=debug)
