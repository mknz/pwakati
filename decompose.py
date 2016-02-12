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

def chunk_with_kanji(istr):
    istr = jctconv.h2z(istr, digit=True, ascii=True)

    t = Tokenizer()
    tokens = t.tokenize(istr)

    # give each element flags (jiritsu or fuzoku)
    flags = [judge_jifu(x.part_of_speech) for x in tokens]
    
    reading = [x.reading.decode('utf-8') for x in tokens]
    surface = [x.surface for x in tokens]

    # split to chunks, delimited by KUGIRI flag
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
        
    return rstr
    
def chunk_with_hira(istr):
    chunks = istr.split(u'　')

    rstr = u''
    t = Tokenizer()
    for c in chunks:
        tokens = t.tokenize(c)
        for tk in tokens:
            rstr += jctconv.kata2hira(tk.reading.decode('utf-8')) + u'　'

    return rstr

def main(istr):
    rstr = chunk_with_hira(chunk_with_kanji(istr))
    return rstr

if __name__ == "__main__":
    f = open('test.txt','r')
    istr = f.read().decode('utf-8')
    print main(istr)

