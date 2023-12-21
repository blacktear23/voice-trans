var onChatText = null;
var onChatError = null;

function chat_message(message) {
    submit_chat(message).then((resp) => {
        if (resp.status == 200) {
            const data = resp.data;
            const text = data.text;
            if (onChatText !== null) {
                onChatText(text);
            }
        } else {
            console.log('Error');
            if (onChatError !== null) {
                onChatError(data);
            }
        }
    }).catch((err) => {
        console.log(err);
        if (onChatError !== null) {
            onChatError(err);
        }
    });
}

function setChatEventListener(event, handler) {
    if (event === 'ontext') {
        onChatText = handler;
    } else if (event === 'onerror') {
        onChatError = handler;
    }
}
