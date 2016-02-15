# -*- coding: utf-8 -*-
import re, sys
import jctconv
from janome.tokenizer import Tokenizer

WTYPE = (
    JIRITSU,
    FUZOKU,
    KUTOU,
    KUGIRI
) = range(4)

TOKENS_KANJI = re.compile(u'[々〇〻\u3220-\u3244\u3280-\u32B0\u3400-\u9FFF\uF900-\uFAFF\u2000-\u2FFF]+') 
TOKENS_KATAKANA = re.compile(u'[ァ-ヾ]+')
TOKENS_HIRAGANA = re.compile(u'[ぁ-ん]+')

# kanji + katakana + hiragana
TOKENS_TARGET = re.compile(u'[々〇〻\u3220-\u3244\u3280-\u32B0\u3400-\u9FFF\uF900-\uFAFF\u2000-\u2FFFァ-ヾぁ-ん]+')

def judge_jifu(part_of_speech):
    try: 
        part_of_speech = part_of_speech.decode('utf-8')
    except:
        pass

    ps = part_of_speech.split(',')
    p1 = ps[0]
    p2 = ps[1]

    if p1 == u'形容詞' and p2 == u'自立':
        return JIRITSU

    elif p1 == u'名詞':
        if p2 == u'非自立':
            return FUZOKU
        else:
            return JIRITSU
        
    elif p1 == u'動詞' and p2 == u'自立':
        return JIRITSU
    elif p1 == u'副詞':
        return JIRITSU
    elif p1 == u'接続詞':
        return JIRITSU
    elif p1 == u'連体詞':
        return JIRITSU
    elif p1 == u'接頭詞':
        return JIRITSU

    elif p1 == u'記号':
        if p2 in [u'句点', u'読点']:
            return KUTOU
        else:
            return JIRITSU

    elif p1 == u'助動詞':
        return FUZOKU
    elif p1 == u'助詞':
        return FUZOKU
    elif p1 == u'動詞' and p2 == u'接尾':
        return FUZOKU
    elif p1 == u'動詞' and p2 == u'非自立':
        return FUZOKU
    elif p1 == u'形容詞' and p2 == u'非自立':
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
        if r == u'*':
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
    rstr = u""
    i = 0
    for j, f in enumerate(flags):
        if i >= len(cflags): break
        if cflags[i] == KUGIRI:
            if f == KUTOU: 
                rstr += surface[j]
                i += 1
            else:
                rstr += u"　"
                rstr += surface[j]
                i += 2
        else:
            rstr += surface[j]
            i += 1

    # don't know why this is necessary
    if flags != [] and j == 0 and len(surface) != 1: 
        while j  < len(surface):
            rstr += surface[j]    
            j += 1

    return rstr
    
def chunk_with_hira(istr, keep_katakana=False):
    t = Tokenizer()
    tokens = t.tokenize(istr)

    readings = [x.reading.decode('utf-8') for x in tokens]
    surfaces = [x.surface for x in tokens]

    pos = []
    for token in tokens:
        p = token.part_of_speech.split(',')[0]
        if isinstance(p, unicode):
            pos.append(p)
        else:
            pos.append(p.decode('utf-8'))

    pos2 = []
    for token in tokens:
        p = token.part_of_speech.split(',')[1]
        if isinstance(p, unicode):
            pos2.append(p)
        else:
            pos2.append(p.decode('utf-8'))

    rstr = u''
    for i, z in enumerate(zip(readings, surfaces, pos, pos2)):
        r, s, p, p2 = z

        if r == u'*':
            if not keep_katakana:
                if re.match(TOKENS_KATAKANA, s):
                    rstr += jctconv.kata2hira(s) + u'　'
                else:
                    rstr += s + u'　'
            else:
                rstr += s + u'　'
            continue

        if i < len(pos) - 1:
            if pos[i] == u'助動詞' and pos[i+1] == u'助動詞':
                rstr += jctconv.kata2hira(r)
            elif pos[i] == u'動詞' and pos[i+1] == u'助動詞':
                rstr += jctconv.kata2hira(r)
            elif pos[i] == u'動詞' and pos[i+1] == u'助詞':
                rstr += jctconv.kata2hira(r)
            elif pos[i] == u'動詞' and pos[i+1] == u'動詞':
                rstr += jctconv.kata2hira(r)
            elif pos2[i] == u'代名詞' and pos2[i+1] == u'副助詞／並立助詞／終助詞':
                rstr += jctconv.kata2hira(r)
            elif pos2[i+1] == u'接尾':
                rstr += jctconv.kata2hira(r)
            else:
                rstr += jctconv.kata2hira(r) + u'　'

        elif i < len(pos) - 2:
            if pos[i] == u'助動詞' and pos[i+1] == u'助詞' and pos[i+2] == u'助詞':
                rstr += jctconv.kata2hira(r)
            elif pos[i] == u'助動詞' and pos[i+1] == u'名詞' and pos[i+2] == u'助動詞':
                rstr += jctconv.kata2hira(r)
            else:
                rstr += jctconv.kata2hira(r) + u'　'

        else:
            rstr += jctconv.kata2hira(r) + u'　'

    '''
    for tk in tokens:
        reading = tk.reading.decode('utf-8')
        if reading == u'*':
            reading = tk.surface
        rstr += jctconv.kata2hira(reading) + u'　'
    '''

    return rstr

def clean_punct(istr):
    ''' remove space before punctuatons '''
    istr = re.sub(ur'　。', u'。', istr)
    istr = re.sub(ur'。　', u'。', istr)
    istr = re.sub(ur'　、', u'、', istr)
    istr = re.sub(ur'、　', u'、', istr)
    istr = re.sub(ur'　！', u'！', istr)
    istr = re.sub(ur'　？', u'？', istr)
    return istr

def add_space_after_punct(istr):
    istr = re.sub(ur'。', u'。　', istr)
    istr = re.sub(ur'、', u'、　', istr)
    return istr

def main(istr, kanji=False):
    lines = istr.splitlines()
    rstr = u''
    for line in lines:
        # split at non-target part, process only target part
        targets = re.findall(TOKENS_TARGET, line)
        non_targets = re.split(TOKENS_TARGET, line)
        wline = u''
        for i, z in enumerate(zip(non_targets, targets + [u''])):
            n, t = z
            if kanji:
                w = chunk_with_kanji(t)
            else:
                w = chunk_with_hira(t)
            if i == 0:
                wline += n + w
            else:
                wline += n + u'　' + w
            
        rstr += clean_punct(wline) + u'\n'

    if kanji == False:
        rstr = add_space_after_punct(rstr)

    return rstr

if __name__ == "__main__":
    f = open('test.txt','r')
    istr = f.read().decode('utf-8')
    print main(istr)

