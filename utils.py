import re
import jieba


re_han = re.compile('([﹒﹔﹖﹗．；。！？]["’”」』]{0,2}|：(?=["‘“「『]{1,2}|$))')
re_en = re.compile('([.?!;])')
re_en_chars = re.compile('[a-zA-Z0-9]')
re_chn_chars = re.compile(u'[\u4e00-\u9fff]')


def split_sentences(text):
    words = jieba.lcut(text)
    ret = []
    sentence = ''
    prev_chn = None
    for word in words:
        sword = word.strip()
        if re_han.match(sword) or re_en.match(sword):
            sentence += word
            ret.append(sentence)
            sentence = ''
            continue

        if re_chn_chars.search(sword) is None and re_en_chars.search(sword) is None:
            sentence += word
            continue

        curr_chn = False
        if re_chn_chars.search(sword):
            curr_chn = True

        if prev_chn is None:
            prev_chn = curr_chn

        if prev_chn != curr_chn:
            ret.append(sentence)
            sentence = word
            prev_chn = curr_chn
            continue
        sentence += word
        prev_chn = curr_chn

    if sentence.strip() != '':
        ret.append(sentence)
    return ret