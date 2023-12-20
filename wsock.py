import io
import os
import uuid
import json
import time
import config
import asyncio
import logging
import websockets
import hashlib
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor


os.environ.setdefault('OMP_NUM_THREADS', '8')
task_executer = ThreadPoolExecutor(max_workers=8)
__tts__ = None


class TTSBuffer(object):
    def __init__(self):
        self.buffer = io.BytesIO()

    def get_pcm(self):
        data = self.buffer.getvalue()
        if len(data) < 44:
            return b''
        return data[44:]

    def get_wav(self):
        return self.buffer.getvalue()


class TTSDriver(object):
    def __init__(self):
        try:
            from TTS.api import TTS
            model = config.TTS_MODEL
            self.tts = TTS(model).to('cpu')
        except Exception:
            self.tts = None

    def text_to_pcm(self, text):
        try:
            fname = hashlib.md5(('%s' % datetime.now()).encode()).hexdigest()
            fpath = '/tmp/tts-%s' % fname
            buf = TTSBuffer()
            self.tts.tts_to_file(text=text, file_path=fpath, pipe_out=buf)
            return buf.get_wav()
        finally:
            if os.path.exists(fpath):
                os.unlink(fpath)

    def split_sentences(self, text):
        if self.tts is None:
            return [text]
        return self.tts.synthesizer.split_into_sentences(text)

    def get_sample_rate(self):
        if self.tts is None:
            return 16000
        return self.tts.synthesizer.output_sample_rate


def get_tts():
    global __tts__
    if __tts__ is None:
        __tts__ = TTSDriver()
    return __tts__


def text_spliter_processor(text):
    pid = os.getpid()
    print(f'PID {pid:<10} Text Spliter Processor')

    tts = get_tts()
    resp = {
        'sample_rate': tts.get_sample_rate(),
        'texts': tts.split_sentences(text),
        'channels': 1,
    }
    print(resp)
    return resp


def tts_processor(text):
    pid = os.getpid()
    print(f'PID {pid:<10} TTS Processor: {text}')
    tts = get_tts()
    return tts.text_to_pcm(text)


def wav_to_aac_processor(wav_data, sample_rate):
    tmp_file = str(uuid.uuid1()).replace('-', '')
    tmp_path = '/tmp/tts-%s.aac' % tmp_file
    try:
        from pydub import AudioSegment
        wav_file = io.BytesIO(wav_data)
        aseg = AudioSegment.from_file(wav_file, format='wav')
        # Re-sample to specified sample rate
        if aseg.frame_rate != sample_rate:
            aseg = aseg.set_frame_rate(sample_rate)
        fp = aseg.export(tmp_path, format='adts')
        return fp.read()
    except Exception as e:
        logging.exception(e)
        return b''
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


async def convert_wav_to_aac(wav_data, sample_rate):
    loop = asyncio.get_running_loop()
    tasks = [loop.run_in_executor(task_executer, wav_to_aac_processor, wav_data, sample_rate)]
    for t in asyncio.as_completed(tasks):
        data = await t
        return data


# Request parameters:
# {
#   'text': string, Request text
#   'format': string (optional), Output format: pcm, wav, aac
#   'sample_rate': int (optional), Output format related sample rate.
# }
def process_request(json_message):
    try:
        jdata = json.loads(json_message)
        return jdata['text'], jdata.get('format', 'pcm'), jdata.get('sample_rate', 1600)
    except Exception as e:
        logging.exception(e)
        return None


async def response_error(wsock, msg):
    jdata = json.dumps({'status': 'error', 'message': msg})
    await wsock.send(jdata)


async def listener(websocket, path):
    if path != '/tts':
        logging.info('404, Invalid Path %s' % path)
        await response_error(websocket, 'Invalid path %s' % path)
        return

    tasks = []
    loop = asyncio.get_running_loop()
    async for json_message in websocket:
        message, out_fmt, out_sample_rate = process_request(json_message)
        if message is None or message == '':
            logging.info('Bad Request: empty text')
            await response_error(websocket, 'Empty text')
            return
        if out_fmt not in ['pcm', 'wav', 'aac']:
            logging.info('Bad Request: unknown format: %s' % out_fmt)
            await response_error(websocket, 'Unknown format: %s' % out_fmt)
            return
        try:
            out_sample_rate = int(out_sample_rate)
        except Exception:
            logging.info('Bad Request: invalid sample_rate: %s' % out_sample_rate)
            await response_error(websocket, 'Invalid sample rate: %s' % out_sample_rate)
            return

        tasks.append(
            loop.run_in_executor(task_executer, text_spliter_processor, message)
        )
        for task in asyncio.as_completed(tasks):
            tinfo = await task
            o_sample_rate = tinfo['sample_rate']
            if out_fmt == 'aac' and out_sample_rate != o_sample_rate:
                sample_rate = out_sample_rate
            else:
                sample_rate = o_sample_rate
            texts = tinfo['texts']
            channels = tinfo['channels']
            await websocket.send(json.dumps({
                'status': 'success',
                'sample_rate': sample_rate,
                'channels': channels,
            }))
            for text in texts:
                ntasks = [
                    loop.run_in_executor(task_executer, tts_processor, text)
                ]
                for nt in asyncio.as_completed(ntasks):
                    data = await nt
                    if out_fmt == 'pcm':
                        if len(data) < 44:
                            break
                        await websocket.send(data[44:])
                    elif out_fmt == 'wav':
                        await websocket.send(data)
                    elif out_fmt == 'aac':
                        aac_data = await convert_wav_to_aac(data, out_sample_rate)
                        await websocket.send(aac_data)
        await websocket.send(b'')
        # Job Done


def run_server(host='0.0.0.0', port=8765):
    try:
        print(f'Listen {host}:{port}')
        start_server = websockets.serve(listener, host, port)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(start_server)
        loop.run_forever()
    except Exception as e:
        print(f'Caught exception {e}')
        pass
    finally:
        loop.close()
