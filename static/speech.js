var recorder = null;
var inRecording = false;
var onStartRecord = null;
var onStopRecord = null;
var onText = null;
var onUploading = null;
var onFinish = null;

function startRecord() {
    if (!recorder) {
        recorder = new Recorder({
            sampleBits: 16,
            sampleRate: 16000,
            numChannels: 1
        });
    }
    recorder.start().then(() => {
        console.log('Start Recording');
        inRecording = true;
        if (onStartRecord !== null) {
            onStartRecord();
        }
    }).catch((err) => {
        alert('Cannot Record:' + err);
        recorder.destroy().then(() => {
            recorder = null;
            inRecording = false;
            if (onStopRecord !== null) {
                onStopRecord();
            }
        });
    });
}

function stopRecord() {
    if (!recorder) {
        alert('Not Support');
        return;
    }
    if (inRecording) {
        recorder.stop();
        console.log('Recording Stopped');
        inRecording = false;
        if (onStopRecord !== null) {
            onStopRecord();
        }
        uploadAndDestroy();
    }
}

function uploadAndDestroy() {
    if (inRecording) {
        return;
    }
    if (recorder) {
        let blob = recorder.getWAVBlob();
        let formData = new FormData();
        formData.append('file', blob);
        if (onUploading !== null) {
            onUploading();
        }
        upload_voice(formData).then((resp) => {
            if (resp.status === 200) {
                const data = resp.data;
                const text = data.text;
                if (onText !== null) {
                    onText(text);
                }
            } else {
                if (onFinish !== null) {
                    onFinish();
                }
            }
        }).catch((err) => {
            if (onFinish !== null) {
                onFinish();
            }
            console.log(err);
            if (err.response.status !== 500) {
                alert(err.response.data.message);
            }
        });
    }
}

function setSpeechEventListener(event, handler) {
    if (event === 'onstart') {
        onStartRecord = handler;
    } else if (event === 'onstop') {
        onStopRecord = handler;
    } else if (event === 'onuploading') {
        onUploading = handler;
    } else if (event === 'onfinish') {
        onFinish = handler;
    } else if (event === 'ontext') {
        onText = handler;
    }
}
