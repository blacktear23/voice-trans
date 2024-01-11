PROMPT_TPLS = [
    {
        'key': 'empty',
        'name': 'Empty',
        'prompt': '',
    },
    {
        'key': 'trans-eng',
        'name': 'Translate to English',
        'prompt': '请把以下句子翻译成英文: {prompt}',
    },
    {
        'key': 'trans-chn',
        'name': 'Translate to Chinese',
        'prompt': '请把以下句子翻译成中文: {prompt}',
    },
    {
        'key': 'suggest-eng',
        'name': 'Give English Suggestion',
        'prompt': '你是一个英语老师，请根据用词，语法评价一下以下句子是否优秀, 如果不优秀，请提供一些建议: {prompt}'
    },
    {
        'key': 'english-teacher',
        'name': 'English Teacher',
        'prompt': '你是一个英语老师，请根据下面的问题进行口语练习回答: {prompt}',
    },
]
