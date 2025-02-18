import json
from ollama import Client


class OllamaAPI(object):
    def __init__(self, host, port, model="qwen2.5"):
        self.client = Client(host='http://%s:%s' % (host, port))
        self.model = model

    def chat(self, msgs, params={}):
        response = self.client.chat(model=self.model,
                                    messages=msgs,
                                    stream=False,
                                    options=self.filter_params(params))
        return response.message

    def filter_params(self, params):
        ret = {}
        keys = [
            ('max_length', 'num_ctx'),
            ('top_k', 'top_k'),
            ('top_p', 'top_p'),
            ('temperature', 'temperature'),
            ('repetition_penalty', 'repeat_penalty')
        ]
        for k, tk in keys:
            if k in params:
                ret[tk] = params[k]
        return ret
