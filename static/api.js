function upload_voice(formData) {
    return axios.post('/speech_translate', formData);
}

function upload_voice_transcribe(formData) {
    return axios.post('/speech_transcribe', formData);
}

function submit_chats(prompts, tpl, histories) {
    return axios.post('/chat_msgs', {'prompts': prompts, 'prompt_template': tpl, 'num_history': histories});
}

function get_prompt_templates() {
    return axios.get('/prompt_templates');
}
