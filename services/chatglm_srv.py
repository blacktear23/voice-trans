import json
from flask import Flask, request, send_file, jsonify, redirect
import config


LLM_MODEL_PATH = config.LLM_MODEL_PATH


glmapp = Flask('chatglm_api')
__chatglm_api__ = None


def get_llm_driver():
    global __chatglm_api__
    if __chatglm_api__ is None:
        try:
            import chatglm_cpp
            __chatglm_api__ = chatglm_cpp.Pipeline(LLM_MODEL_PATH)
        except Exception:
            pass
    return __chatglm_api__


@glmapp.route('/chat', methods=['POST'])
def glmapp_chat():
    data = request.json
    messages = data.get('messages', [])
    if len(messages) == 0:
        return 'Require messages parameter', 400

    llm = get_llm_driver()
    if llm is None:
        return 'Cannot Load LLM driver', 500

    params = get_parameters(data)
    msgs = build_messages(messages)
    output = ''
    first = True
    for chunk in llm.chat(msgs, **params):
        if first and '\n' in chunk.content:
            first = False
            output += remove_prefix(chunk.content, '\n')
        else:
            output += chunk.content
    return jsonify({'text': output})


def build_messages(messages):
    import chatglm_cpp
    ret = []
    for msg in messages:
        role = msg.get('role', 'user')
        item = None
        if role == 'user':
            item = chatglm_cpp.ChatMessage('user', msg.get('content', ''))
        elif role == 'assistant':
            item = chatglm_cpp.ChatMessage('assistant', msg.get('content', ''))

        if item is not None:
            ret.append(item)
    return ret


def get_parameters(data):
    params = {
        'max_length': data.get('max_length', 4096),
        'max_context_length': data.get('max_content_length', 2048),
        'do_sample': data.get('do_sample', True),
        'top_k': data.get('top_k', 0),
        'top_p': data.get('top_p', 0.7),
        'temperature': data.get('temperature', 0.95),
        'repetition_penalty': data.get('repetition_penalty', 1.0),
        'stream': True,
    }
    return params


def remove_prefix(val, prefix):
    if val.startswith(prefix):
        return val[len(prefix):]
    return val


def run_chatglm_api(host='127.0.0.1', port=8889, debug=True):
    glmapp.run(host=host, port=port, debug=debug)
