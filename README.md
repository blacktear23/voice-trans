# Voice Translator

It using Whisper and TTS to translate Chinese into English and speak it out.

# Install

## Install Python Packages

```
pip3 install -r requirements
```

## Download Models

**For Whisper Models:**

```
wget https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-medium.bin
```

Or you can download from `https://huggingface.co/ggerganov/whisper.cpp/tree/main`


**For TTS Models**

```
tts --text 'This is a test' --model_name 'tts_models/en/ljspeech/vits' --out_path /tmp/test.wav
```

You can use `tts --list_models` command to find available models

# Run it

copy `config.py.example` to `config.py` and then update `config.py` to tell application which TTS model will be used and where's Whisper model file is.

```
WHISPER_MODEL_PATH = '[Whisper Model Path]'
TTS_MODEL = '[TTS Model Name]'
```

Then start the server

```
python3 main.py
```

The server will listen 7880 for Web server and 7881 for WebSocket server

After server started, use Chrome browser open `http://127.0.0.1:7880`

## Technologies

* Speech Recognition and translate: Whisper.cpp and whisper-cpp-python
* Speech to Text: coqui-ai/TTS
* Web and WebSocket: flask, websockets
