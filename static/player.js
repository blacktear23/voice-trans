var player = null;
var aid = 0;
var audioFinish = false;
var hasAudioData = false;
var onStartPlay = null;
var onStopPlay = null;
var ws = null;

function startPlay(url, parameter) {
    aid++;
    var caid = aid;
    audioFinish = false;
    // Build player
    if (player !== null) {
        player.destroy();
        player = null;
    }
    player = new PCMPlayer({
        encoding: '16bitFloat',
        channels: 1,
        sampleRate: 16000,
        flushingTime: 500,
        onended: function() {
            var checker = setInterval(function() {
                try {
                    if (player === null || player.audioCtx === null) {
                        // Closed by others
                        clearInterval(checker);
                        return;
                    }
                    if (audioFinish && player.samples.length <= 0 && player.audioCtx.currentTime > player.startTime) {
                        console.log('Play Finished');
                        clearInterval(checker);
                        player.destroy();
                        player = null;
                        if (onStopPlay !== null) {
                            onStopPlay();
                        }
                    }
                } catch(err) {
                    console.log(err);
                    clearInterval(checker)
                }
            }, 200);
        }
    });
    player.volume(2);

    // Build Websocket
    if (ws !== null) {
        ws.close();
        ws = null;
    }
    ws = new WebSocket(url);
    hasAudioData = false;
    ws.binaryType = 'arraybuffer';
    // Set ws message handler
    var firstMsg = true;
    ws.addEventListener('message', (event) => {
        console.log('On Message');
        if (firstMsg) {
            firstMsg = false;
            if (typeof event.data === 'string' || event.data instanceof String) {
                // First message update player settings
                try {
                    var dinfo = JSON.parse(event.data);
                    player.option.sampleRate = dinfo['sample_rate'];
                    player.option.channels = dinfo['channels'];
                    console.log(player.option);
                } catch(err) {
                    console.log(err);
                }
                return;
            } else {
                try {
                    var decoder = new TextDecoder("utf-8");
                    var dtext = decoder.decode(event.data)
                    var dinfo = JSON.parse(dtext);
                    player.option.sampleRate = dinfo['sample_rate'];
                    player.option.channels = dinfo['channels'];
                    console.log(player.option);
                } catch(err) {
                    console.log(err);
                }
                return;
            }
        }
        // Empty data just stop play
        if (event.data.byteLength === 0) {
            // End
            if (aid === caid) {
                ws.close()
                audioFinish = true;
                if (!hasAudioData) {
                    player.destroy();
                    player = null;
                    console.log('Stop Player');
                    if (onStopPlay !== null) {
                        onStopPlay();
                    }
                }
            }
            console.log('End');
            return;
        }
        // Write data to player
        if (aid === caid) {
            var data = new Uint8Array(event.data);
            if (player !== null) {
                player.feed(data);
                hasAudioData = true;
                if (onStartPlay !== null) {
                    onStartPlay();
                }
            }
        }
    });
    // Set ws open handler
    ws.onopen = function() {
        console.log('On Open');
        console.log(parameter);
        ws.send(JSON.stringify(parameter));
    }
    // Set ws close handler
    ws.onclose = function() {
        console.log('On Close');
        if (aid === caid) {
            ws = null;
            audioFinish = true;
        }
    }
}

function stopPlay() {
    if (ws !== null) {
        ws.close();
    }
    if (player !== null) {
        player.destroy();
    }
    player = null;
    ws = null;
}

function setPlayerEventListener(event, handler) {
    if (event === 'onstartplay') {
        onStartPlay = handler;
    } else if (event === 'onstopplay') {
        onStopPlay = handler;
    }
}
