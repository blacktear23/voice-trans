function upload_voice(formData) {
    return axios.post('/speech_translate', formData);
}

function upload_voice_transcribe(formData) {
    return axios.post('/speech_transcribe', formData);
}

function submit_chat(text, tpl) {
    return axios.post('/chat_msg', {'prompt': text, 'prompt_template': tpl});
}
