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

TOKENS_KANJI = re.compile(u'[一-龠]+') 
TOKENS_KATAKANA = re.compile(u'[ァ-ヾ]+')
TOKENS_HIRAGANA = re.compile(u'[[ぁ-ん]+')

# kanji + katakana + hiragana
TOKENS_TARGET = re.compile(u'[一-龠ァ-ヾぁ-ん]+')

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
        print p1, p2
        raise

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
    if flags != [] and j == 0: 
        while j  < len(surface):
            rstr += surface[j]    
            j += 1

    return rstr
    
def chunk_with_hira(istr):
    chunks = istr.split(u'　')

    rstr = u''
    t = Tokenizer()
    for c in chunks:
        tokens = t.tokenize(c)
        for tk in tokens:
            reading = tk.reading.decode('utf-8')
            if reading == u'*':
                reading = tk.surface
            rstr += jctconv.kata2hira(reading) + u'　'

    return rstr

def clean_punct(istr):
    ''' remove space before punctuatons '''
    istr = re.sub(ur'　。', u'。', istr)
    istr = re.sub(ur'。　', u'。', istr)
    istr = re.sub(ur'　、', u'、', istr)
    istr = re.sub(ur'、　', u'、', istr)
    return istr

def main(istr):
    lines = istr.splitlines()
    rstr = u''
    for line in lines:
        # split at non-target part, process only target part
        targets = re.findall(TOKENS_TARGET, line)
        non_targets = re.split(TOKENS_TARGET, line)
        wline = u''
        for n, t in zip(non_targets, targets + [u'']):
            w = chunk_with_hira(chunk_with_kanji(t))
            wline += n + w
            
        rstr += clean_punct(wline) + u'\n'

    return rstr

if __name__ == "__main__":
    f = open('test.txt','r')
    istr = f.read().decode('utf-8')
    print main(istr)

