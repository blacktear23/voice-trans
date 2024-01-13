var onChatText = null;
var onChatError = null;

function chat_message(message, tpl) {
    submit_chat(message, tpl).then((resp) => {
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

function chat_messages(prompts, tpl, histories) {
    submit_chats(prompts, tpl, histories).then((resp) => {
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

var prebuild_prompt_templates = {
    'empty': ['', 5],
    'trans-eng': ['请把以下句子翻译成英文: {prompt}', 1],
    'trans-chn': ['请把以下句子翻译成中文: {prompt}', 1],
}

function get_prebuild_prompt_template(key) {
    if (prebuild_prompt_templates.hasOwnProperty(key)) {
        return prebuild_prompt_templates[key];
    }
    return null;
}
