# -*- coding: utf-8 -*-
import re

from janome.tokenizer import Tokenizer
import jctconv

WTYPE = (
    JIRITSU,
    FUZOKU,
    KUTOU,
    KUGIRI
) = range(4)

TOKENS_KANJI = re.compile('[々〇〻\u3220-\u3244\u3280-\u32B0\u3400-\u9FFF\uF900-\uFAFF\u2000-\u2FFF]+')
TOKENS_KATAKANA = re.compile('[ァ-ヾ]+')
TOKENS_HIRAGANA = re.compile('[ぁ-ん]+')

# kanji + katakana + hiragana
TOKENS_TARGET = re.compile('[々〇〻\u3220-\u3244\u3280-\u32B0\u3400-\u9FFF\uF900-\uFAFF\u2000-\u2FFFァ-ヾぁ-ん]+')


def judge_jifu(part_of_speech):
    try:
        part_of_speech = part_of_speech.decode('utf-8')
    except:
        pass

    ps = part_of_speech.split(',')
    p1 = ps[0]
    p2 = ps[1]

    if p1 == '形容詞' and p2 == '自立':
        return JIRITSU

    elif p1 == '名詞':
        if p2 == '非自立':
            return FUZOKU
        else:
            return JIRITSU

    elif p1 == '動詞' and p2 == '自立':
        return JIRITSU
    elif p1 == '副詞':
        return JIRITSU
    elif p1 == '接続詞':
        return JIRITSU
    elif p1 == '連体詞':
        return JIRITSU
    elif p1 == '接頭詞':
        return JIRITSU

    elif p1 == '記号':
        if p2 in ['句点', '読点']:
            return KUTOU
        else:
            return JIRITSU

    elif p1 == '助動詞':
        return FUZOKU
    elif p1 == '助詞':
        return FUZOKU
    elif p1 == '動詞' and p2 == '接尾':
        return FUZOKU
    elif p1 == '動詞' and p2 == '非自立':
        return FUZOKU
    elif p1 == '形容詞' and p2 == '非自立':
        return FUZOKU
    else:
        return JIRITSU


def insert_chunkflg(flags):
    s = ''
    for f in flags:
        s += str(f)
    l = re.findall(r'%s+%s*' % (JIRITSU, FUZOKU), s)
    result = []
    for ll in l:
        for lll in ll:
            result.append(int(lll))
        result.append(KUGIRI)

    return result


def fix_reading(surfaces, readings):
    rn = []
    for s, r in zip(surfaces, readings):
        if r == '*':
            rn.append(s)
        else:
            rn.append(r)
    return rn


def chunk_with_kanji(istr):
    t = Tokenizer()
    tokens = t.tokenize(istr)

    # give each element flags (jiritsu or fuzoku)
    flags = [judge_jifu(x.part_of_speech) for x in tokens]

    surface = [x.surface for x in tokens]

    # split to chunks, delimited by KUGIRI flag
    # very ugly. should be rewritten using tree structure etc.
    cflags = insert_chunkflg(flags)
    rstr = ''
    i = 0
    for j, f in enumerate(flags):
        if i >= len(cflags):
            break

        if cflags[i] == KUGIRI:
            if f == KUTOU:
                rstr += surface[j]
                i += 1
            else:
                rstr += '　'
                rstr += surface[j]
                i += 2
        else:
            rstr += surface[j]
            i += 1

    # don't know why this is necessary
    if flags != [] and j == 0 and len(surface) != 1:
        while j < len(surface):
            rstr += surface[j]
            j += 1

    return rstr


def chunk_with_hira(istr, keep_katakana=False):
    t = Tokenizer()
    tokens = t.tokenize(istr)

    readings = []
    for token in tokens:
        reading = token.reading
        readings.append(reading)

    surfaces = [x.surface for x in tokens]

    pos = []
    for token in tokens:
        p = token.part_of_speech.split(',')[0]
        pos.append(p)

    pos2 = []
    for token in tokens:
        p = token.part_of_speech.split(',')[1]
        pos2.append(p)

    rstr = ''
    for i, z in enumerate(zip(readings, surfaces, pos, pos2)):
        r, s, p, p2 = z

        if r == '*':
            if not keep_katakana:
                if re.match(TOKENS_KATAKANA, s):
                    rstr += jctconv.kata2hira(s) + '　'
                else:
                    rstr += s + '　'
            else:
                rstr += s + '　'
            continue

        if i < len(pos) - 1:
            if pos[i] == '助動詞' and pos[i+1] == '助動詞':
                rstr += jctconv.kata2hira(r)
            elif pos[i] == '動詞' and pos[i+1] == '助動詞':
                rstr += jctconv.kata2hira(r)
            elif pos[i] == '動詞' and pos[i+1] == '助詞':
                rstr += jctconv.kata2hira(r)
            elif pos[i] == '動詞' and pos[i+1] == '動詞':
                rstr += jctconv.kata2hira(r)
            elif pos[i] == '接頭詞' and pos[i+1] == '名詞':
                rstr += jctconv.kata2hira(r)
            elif pos2[i] == '代名詞' and pos2[i+1] == '副助詞／並立助詞／終助詞':
                rstr += jctconv.kata2hira(r)
            elif pos2[i+1] == '接尾':
                rstr += jctconv.kata2hira(r)
            else:
                rstr += jctconv.kata2hira(r) + '　'

        elif i < len(pos) - 2:
            if pos[i] == '助動詞' and pos[i+1] == '助詞' and pos[i+2] == '助詞':
                rstr += jctconv.kata2hira(r)
            elif pos[i] == '助動詞' and pos[i+1] == '名詞' and pos[i+2] == '助動詞':
                rstr += jctconv.kata2hira(r)
            else:
                rstr += jctconv.kata2hira(r) + '　'

        else:
            rstr += jctconv.kata2hira(r) + '　'

    return rstr


def remove_space(istr):
    '''remove space before punctuatons'''

    replace_strings_before = '。、！？（「【『［〈《〔｛《＜“‘'
    replace_strings_after = '。、！？）」】』］〉》〕｝》＞”’'

    for rs in replace_strings_before:
        istr = re.sub(r'%s　' % rs, r'%s' % rs, istr)

    for rs in replace_strings_after:
        istr = re.sub(r'　%s' % rs, r'%s' % rs, istr)

    return istr


def add_space_after_punct(istr):
    istr = re.sub(r'。', '。　', istr)
    istr = re.sub(r'。　\n', '。\n', istr)
    istr = re.sub(r'、', '、　', istr)
    return istr


def main(istr, kanji=False, keep_katakana=False):
    lines = istr.splitlines()
    rstr = ''
    for line in lines:
        # split at non-target part, process only target part
        targets = re.findall(TOKENS_TARGET, line)
        non_targets = re.split(TOKENS_TARGET, line)
        wline = ''
        for i, z in enumerate(zip(non_targets, targets + [''])):
            n, t = z
            if kanji:
                w = chunk_with_kanji(t)
            else:
                w = chunk_with_hira(t, keep_katakana=keep_katakana)
            if i == 0:
                wline += n + w
            else:
                wline += n + '　' + w

        if wline != '':
            while 1:  # remove spaces at the end of the line
                if wline[-1] == '　':
                    wline = wline[:-1]
                else:
                    break

        rstr += remove_space(wline) + '\n'

    if rstr != '':
        while True:  # remove newline at the end of the line
            if rstr[-1] == '\n':
                rstr = rstr[:-1]
            else:
                break

    if not kanji:
        rstr = add_space_after_punct(rstr)
        if rstr != '':
            while True:  # remove space at the end of the line
                if rstr[-1] == '　':
                    rstr = rstr[:-1]
                else:
                    break
    return rstr
