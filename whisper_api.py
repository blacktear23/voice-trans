import json
import requests


class WhisperAPI(object):
    WHISPER_SR = 16000

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.url = f'http://{host}:{port}/inference'

    def translate(self, wav_file, prompt='', lang='auto'):
        params = {
            'translate': 'true',
            'language': lang,
            'prompt': prompt,
        }
        files = {'file': wav_file}
        resp = requests.post(self.url, files=files, data=params)
        if resp.status_code == 200:
            content = json.loads(resp.content)
            return content
        else:
            raise Exception(resp.content)

    def transcribe(self, wav_file, prompt='', lang='auto'):
        params = {
            'translate': 'false',
            'language': lang,
            'prompt': prompt,
        }
        files = {'file': wav_file}
        resp = requests.post(self.url, files=files, data=params)
        if resp.status_code == 200:
            content = json.loads(resp.content)
            return content
        else:
            raise Exception(resp.content)
