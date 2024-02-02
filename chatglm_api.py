import json
import requests


class ChatGLMAPI(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.url = f'http://{host}:{port}/chat'

    def chat(self, msgs, params={}):
        params['messages'] = msgs
        jparams = json.dumps(params)
        headers = {'Content-Type': 'application/json'}
        resp = requests.post(self.url, data=jparams, headers=headers)
        if resp.status_code == 200:
            ret = json.loads(resp.content)
            return ret
        else:
            raise Exception(resp.content)
