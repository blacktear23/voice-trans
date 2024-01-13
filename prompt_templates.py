PROMPT_TPLS = [
    {
        'key': 'empty',
        'name': 'Scenes',
        'prompt': '',
        'history': 1,
    },
    {
        'key': 'trans-eng',
        'name': 'Translate to English',
        'prompt': '请把以下句子翻译成英文: {prompt}',
        'history': 1,
    },
    {
        'key': 'trans-chn',
        'name': 'Translate to Chinese',
        'prompt': '请把以下句子翻译成中文: {prompt}',
        'history': 1,
    },
    {
        'key': 'suggest-eng',
        'name': 'Give English Suggestion',
        'prompt': '你是一个英语老师，请根据用词，语法评价一下以下句子是否优秀, 如果不优秀，请提供一些建议: {prompt}',
        'history': 1,
    },
    {
        'key': 'english-teacher',
        'name': 'English Teacher',
        'prompt': '你是一个英语老师，你只回答英文，请根据下面的问题进行英语口语练习回答: {prompt}',
        'history': 5,
    },
    {
        'key': 'assis-talk',
        'name': 'Assistant Talk',
        'prompt': '你是一个智能助理，根据提出的问题进行回答，以下为问题的搜索结果:\n{search_ctx}\n\n请总结搜索结果并回答问题，如果你能直接回答问题则忽略搜索结果，记住你只回答英文，以下为问题:\n{prompt}',
        'history': 1,
    },
]
