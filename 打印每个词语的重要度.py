import collections
import termextract.japanese_plaintext
import termextract.core
import re
import MeCab

# ファイルを読み込む
text = open(r"../testMecab/text2.txt", "r", encoding="utf-8").read()
TOTAL_MARK = "."  # トータル文書数を示す"."をセット
OTAL_MARK = "."  # トータル文書数を示す"."をセット
IGNORE_WORDS = set([])  # 重要度計算外とする語
no_need_words = ["これ","ここ","こと","それ","ため","よう","さん","そこ","たち","ところ","それぞれ","これら","どれ","br"]

# ひらがな
JP_HIRA = set([chr(i) for i in range(12353, 12436)])
# カタカナ
JP_KATA = set([chr(i) for i in range(12449, 12532+1)])
JP_KATA.add('ー')
#要忽略的字符
# "ー"特殊
MULTIBYTE_MARK = set([
    '、', ',', '，', '。', '．','\'', '”', '“', '《', '》', '：', '（', '）', '(', ')', '；', '.', '・', '～', '`',
    '%', '％', '$', '￥', '~', '■', '●', '◆', '×', '※', '►', '▲', '▼', '‣', '·', '∶', ':', '‐', '_', '‼', '≫',
    '－', ';', '･', '〈', '〉', '「', '」', '『', '』', '【', '】', '〔', '〕', '?', '？', '!', '！', '+', '-',
    '*', '÷', '±', '…', '‘', '’', '／', '/', '<', '>', '><', '[', ']', '#', '＃', '゛', '゜',
    # '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
    # '０','１', '２', '３', '４', '５', '６', '７', '８', '９',
    '①', '②', '③', '④', '⑤', '⑥', '⑦', '⑧', '⑨',
    '⑩', '⑪', '⑫', '⑬', '⑭', '⑮', '⑯', '⑰', '⑱', '⑲', '⑳',
    '➀', '➁', '➂', '➃', '➄', '➅', '➆', '➇', '➈', '➉',
    '⑴', '⑵', '⑶', '⑷', '⑸', '⑹', '⑺', '⑻', '⑼', '⑽',
    '⑾', '⑿', '⒀', '⒁', '⒂', '⒃', '⒄', '⒅', '⒆', '⒇',
    '⒈', '⒉', '⒊', '⒋', '⒌', '⒍', '⒎', '⒏', '⒐', '⒑',
    '⒒', '⒓', '⒔', '⒕', '⒖', '⒗', '⒘', '⒙', '⒚', '⒛',
    'ⅰ', 'ⅱ', 'ⅲ', 'ⅳ', 'ⅴ', 'ⅵ', 'ⅶ', 'ⅷ', 'ⅸ', 'ⅹ',
    'Ⅰ', 'Ⅱ', 'Ⅲ', 'Ⅳ', 'Ⅴ', 'Ⅵ', 'Ⅶ', 'Ⅷ', 'Ⅸ', 'Ⅹ',
    'Ⅺ', 'Ⅻ', '❶', '❷', '❸', '❹', '❺', '❻', '❼', '❽', '❾', '❿',
    '⓫', '⓬', '⓭', '⓮', '⓯', '⓰', '⓱', '⓲', '⓳', '⓴',
    '㈠', '㈡', '㈢', '㈣', '㈤', '㈥', '㈦', '㈧', '㈨', '㈩',
    '㊀', '㊁', '㊂', '㊃', '㊄', '㊅', '㊆', '㊇', '㊈', '㊉',
    'Ⓐ', 'Ⓑ', 'Ⓒ', 'Ⓓ', 'Ⓔ', 'Ⓕ', 'Ⓖ', 'Ⓗ', 'Ⓘ', 'Ⓙ',
    'Ⓚ', 'Ⓛ', 'Ⓜ', 'Ⓝ', 'Ⓞ', 'Ⓟ', 'Ⓠ', 'Ⓡ', 'Ⓢ', 'Ⓣ',
    'Ⓤ', 'Ⓥ', 'Ⓦ', 'Ⓧ', 'Ⓨ', 'Ⓩ', 'ⓐ', 'ⓑ', 'ⓒ', 'ⓓ',
    'ⓔ', 'ⓕ', 'ⓖ', 'ⓗ', 'ⓘ', 'ⓙ', 'ⓚ', 'ⓛ', 'ⓜ', 'ⓝ',
    'ⓞ', 'ⓟ', 'ⓠ', 'ⓡ', 'ⓢ', 'ⓣ', 'ⓤ', 'ⓥ', 'ⓦ', 'ⓧ',
    'ⓨ', 'ⓩ', '⒜', '⒝', '⒞', '⒟', '⒠', '⒡', '⒢', '⒣',
    '⒤', '⒥', '⒦', '⒧', '⒨', '⒩', '⒪', '⒫', '⒬', '⒭',
    '⒮', '⒯', '⒰', '⒱', '⒲', '⒳', '⒴', '⒵',
    '\r\n', '\t', '\n', '\\',
    '◇', '＜', '＞', '＊', '＝', '◍', '＋', '○', '―', 'ˇ', 'ˉ',
    '¨', '〃', '—', '‖', '∧', '∨', '∑', '∏', '∪', '∩', '∈',
    '∷', '√', '⊥', '∥', '∠', '⌒', '⊙', '∫', '∮', '≡', '≌',
    '≈', '∽', '∝', '≠', '≮', '≯', '≤', '≥', '∞', '∵', '∴',
    '♂', '♀', '°', '′', '″', '℃', '＄', '¤', '￠', '￡', '‰',
    '§', '№', '☆', '★', '□', '〓', '〜', '⬜', '〇', '＿',
    '▢', '∟', '⇒', '◯', '△', '✕', '＆', '|', '＠', '@', '&',
    '〖', '〗', '◎', '〒', '℉', '﹪', '﹫', '㎡', '㏕', '㎜',
    '㎝', '㎞', '㏎', 'm', '㎎', '㎏', '㏄', 'º', '¹', '²', '³',
    '↑', '↓', '←', '→', '↖', '↗', '↘', '↙', '↔', '↕', '➻', '➼',
    '➽', '➸', '➳', '➺', '➴', '➵', '➶', '➷', '➹', '▶', '▷',
    '◁', '◀', '◄', '«', '»', '➩', '➪', '➫', '➬', '➭', '➮',
    '➯', '➱', '⏎', '➲', '➾', '➔', '➘', '➙', '➚', '➛', '➜',
    '➝', '➞', '➟', '➠', '➡', '➢', '➣', '➤', '➥', '➦', '➧',
    '➨', '↚', '↛', '↜', '↝', '↞', '↟', '↠', '↡', '↢', '↣', '↤', '↥',
    '↦', '↧', '↨', '⇄', '⇅', '⇆', '⇇', '⇈', '⇉', '⇊', '⇋', '⇌', '⇍',
    '⇎', '⇏', '⇐', '⇑', '⇓', '⇔', '⇖', '⇗', '⇘', '⇙', '⇜', '↩', '↪',
    '↫', '↬', '↭', '↮', '↯', '↰', '↱', '↲', '↳', '↴', '↵', '↶', '↷',
    '↸', '↹', '☇', '☈', '↼', '↽', '↾', '↿', '⇀', '⇁', '⇂', '⇃', '⇞',
    '⇟', '⇠', '⇡', '⇢', '⇣', '⇤', '⇥', '⇦', '⇧', '⇨', '⇩', '⇪', '↺',
    '↻', '⇚', '⇛', '♐', '┌', '┍', '┎', '┏', '┐', '┑', '┒', '┓', '└', '┕',
    '┖', '┗', '┘', '┙', '┚', '┛', '├', '┝', '┞', '┟', '┠', '┡', '┢', '┣',
    '┤', '┥', '┦', '┧', '┨', '┩', '┪', '┫', '┬', '┭', '┮', '┯', '┰', '┱',
    '┲', '┳', '┴', '┵', '┶', '┷', '┸', '┹', '┺', '┻', '┼', '┽', '┾', '┿',
    '╀', '╁', '╂', '╃', '╄', '╅', '╆', '╇', '╈', '╉', '╊', '╋', '╌', '╍',
    '╎', '╏', '═', '║', '╒', '╓', '╔', '╕', '╖', '╗', '╘', '╙', '╚', '╛',
    '╜', '╝', '╞', '╟', '╠', '╡', '╢', '╣', '╤', '╥', '╦', '╧', '╨', '╩',
    '╪', '╫', '╬', '◤', '◥', '◣', '◢', '▸', '◂', '▴', '▾', '▽', '⊿', '▻',
    '◅', '▵', '▿', '▹', '◃', '❏', '❐', '❑', '❒', '▀', '▁', '▂', '▃', '▄',
    '▅', '▆', '▇', '▉', '▊', '▋', '█', '▌', '▍', '▎', '▏', '▐', '░', '▒', '▓',
    '▔', '▕', '▣', '▤', '▥', '▦', '▧', '▨', '▩', '▪', '▫', '▬', '▭', '▮', '▯',
    '㋀', '㋁', '㋂', '㋃', '㋄', '㋅', '㋆', '㋇', '㋈', '㋉', '㋊', '㋋',
    '㏠', '㏡', '㏢', '㏣', '㏤', '㏥', '㏦', '㏧', '㏨', '㏩', '㏪', '㏫',
    '㏬', '㏭', '㏮', '㏯', '㏰', '㏱', '㏲', '㏳', '㏴', '㏵', '㏶', '㏷',
    '㏸', '㏹', '㏺', '㏻', '㏼', '㏽', '㏾', '㍙', '㍚', '㍛', '㍜', '㍝',
    '㍞', '㍟', '㍠', '㍡', '㍢', '㍣', '㍤', '㍥', '㍦', '㍧', '㍨', '㍩',
    '㍪', '㍫', '㍬', '㍭', '㍮', '㍯', '㍰', '㍘', '☰', '☲', '☱', '☴',
    '☵', '☶', '☳', '☷', '☯', '♠', '♣', '♧', '♡', '♥', '❤', '❥', '❣',
    '✲', '☀', '☼', '☾', '☽', '◐', '◑', '☺', '☻', '☎', '☏', '✿', '❀',
    '¿', '½', '✡', '㍿', '卍', '卐', '✚', '♪', '♫', '♩', '♬', '㊚', '㊛',
    '囍', '㊒', '㊖', 'Φ', 'Ψ', '♭', '♯', '♮', '¶', '€', '¥', '﹢', '﹣',
    '=', '≦', '≧', '≒', '﹤', '﹥', '㏒', '㏑', '⅟', '⅓', '⅕', '⅙',
    '⅛', '⅔', '⅖', '⅚', '⅜', '¾', '⅗', '⅝', '⅞', '⅘', '≂', '≃', '≄',
    '≅', '≆', '≇', '≉', '≊', '≋', '≍', '≎', '≏', '≐', '≑', '≓', '≔',
    '≕', '≖', '≗', '≘', '≙', '≚', '≛', '≜', '≝', '≞', '≟', '≢', '≣',
    '≨', '≩', '⊰', '⊱', '⋛', '⋚', '∬', '∭', '∯', '∰', '∱', '∲', '∳',
    '℅', '‱', 'ø', 'Ø', 'π', 'ღ', '♤', '＇', '〝', '〞', 'ˆ', '﹕', '︰',
    '﹔', '﹖', '﹑', '•', '¸', '´', '｜', '＂', '｀', '¡', '﹏', '﹋',
    '﹌', '︴', '﹟', '﹩', '﹠', '﹡', '﹦', '￣', '¯', '﹨', '˜', '﹍', '﹎',
    '﹉', '﹊', '‹', '›', '﹛', '﹜', '［', '］', '{', '}', '︵', '︷', '︿',
    '︹', '︽', '﹁', '﹃', '︻', '︶', '︸', '﹀', '︺', '︾', '﹂', '﹄',
    '︼', '❝', '❞', '£', 'Ұ', '₴', '₰', '¢', '₤', '₳', '₲', '₪', '₵',
    '₣', '₱', '฿', '₡', '₮', '₭', '₩', 'ރ', '₢', '₥', '₫', '₦',
    'z', 'ł', '﷼', '₠', '₧', '₯', '₨', 'K', 'č', 'र', '₹', 'ƒ', '₸',
    '✐', '✎', '✏', '✑', '✒', '✍', '✉', '✁', '✂', '✃', '✄', '✆',
    '☑', '✓', '✔', '☐', '☒', '✗', '✘', 'ㄨ', '✖', '☢', '☠', '☣', '✈',
    '☜', '☞', '☝', '☚', '☛', '☟', '✌', '♢', '♦', '☁', '☂', '❄', '☃',
    '♨', '웃', '유', '❖', '☪', '✪', '✯', '☭', '✙', '⚘', '♔', '♕', '♖',
    '♗', '♘', '♙', '♚', '♛', '♜', '♝', '♞', '♟', '◊', '◦', '◘', '◈', 'の',
    'Ю', '❈', '✣', '✤', '✥', '✦', '❉', '❦', '❧', '❃', '❂', '❁', '☄', '☊',
    '☋', '☌', '☍', '۰', '⊕', 'Θ', '㊣', '◙', '♈', '큐', '™', '◕', '‿', '｡'
    # "a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z",
    # "A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"
    ])


'''
def cmp_noun_list(data):
    """
    和文テキストを受け取り、複合語（空白区切りの単名詞）のリストを返す
    """
    cmp_nouns = []
    # 行レベルのループ
    for morph in data.split("\n"):
        morph.rstrip()
        terms = []
        if len(morph) == 0:
            continue
        # morph = morph.replace(",", " ")
        # morph = morph.replace(".", " ")
        # morph = morph.replace("(", " ")
        # morph = morph.replace(")", " ")
        # morph = morph.replace(";", " ")
        # morph = morph.replace("!", " ")
        # morph = morph.replace("[", " ")
        # morph = morph.replace("]", " ")
        # morph = morph.replace("?", " ")
        # morph = morph.replace("/", " ")
        is_kata = 0
        kata = ""
        while len(morph) > 1:
            is_stopword = 0
            # 英語
            eng_word = re.match(r"[a-zA-Z0-9_]+", morph)
            if eng_word is not None:
                if is_kata:
                    if len(kata) > 1:
                        terms.append(kata)
                    kata = ""
                    is_kata = 0
                morph = morph[len(eng_word.group(0)):]
                terms.append(eng_word.group(0))
                # _increase(cmp_nouns, terms)
                is_stopword = 0
            if not len(morph) > 1:
                continue
            # マルチバイト記号
            if morph[0] in MULTIBYTE_MARK:
                if is_kata:
                    if len(kata) > 1:
                        terms.append(kata)
                    kata = ""
                    is_kata = 0
                _increase(cmp_nouns, terms)
                is_stopword = 1
            # ひらがな
            if morph[0] in JP_HIRA:
                if is_kata:
                    if len(kata) > 1:
                        terms.append(kata)
                    kata = ""
                    is_kata = 0
                _increase(cmp_nouns, terms)
                is_stopword = 1
            # カタカナ
            if morph[0] in JP_KATA:
                kata += morph[0]
                is_kata = 1##########test0
            if not is_stopword:
                if not is_kata:
                    terms.append(morph[0])
            morph = morph[1:]
    # 行の末尾の処理
    _increase(cmp_nouns, terms)
    return cmp_nouns
'''


def cmp_noun_list(data):
    """
    和文テキストを受け取り、複合語（空白区切りの単名詞）のリストを返す
    """
    savetxt_list=[]
    mecab = MeCab.Tagger("-Ochasen") #有词性标注的
    # mecab = MeCab.Tagger("-Owakati")  # 没有词性标注的
    # data = data.replace("<br/>", "")
    # data = data.replace("<br>", "")
    cmp_nouns = mecab.parse(data)
    every_row = cmp_nouns.split('\n')
    '''
    for every_attribute_line in every_row:
        every_attribute_array = every_attribute_line.split('\t')
        if len(every_attribute_array)>3:
            if every_attribute_array[3].find('名詞') != -1:  # 能在这个属性中找到名词
                if (every_attribute_array[0] and len(every_attribute_array[0].strip()) > 1 and not (every_attribute_array[0].strip().isdigit()) and every_attribute_array[0].strip()[0] not in MULTIBYTE_MARK):
                    savetxt_list.append(every_attribute_array[0])
    savetxt_list = [' '.join(i) for i in savetxt_list]#不加这一句,重要度就是频率
    cmp_nouns = savetxt_list
    return cmp_nouns
    '''

    '''
    # 1295万に対し2099万（予算比162.1％）予算乖離 + 804万 < br / > 部門別予測 < br / >
    str_word_in_front = ''
    # next_is_noun = False #下一个元素是名词
    has_number = False #有数字
    for every_attribute_line in every_row:
        every_attribute_array = every_attribute_line.split('\t')
        if len(every_attribute_array)>3:
            if every_attribute_array[3].find('名詞') != -1 :  # 能在这个属性中找到名词
                if every_attribute_array[3].find('名詞-数') != -1:
                    str_word_in_front += every_attribute_array[0]
                    has_number = True
                    continue
                if has_number==True:
                    savetxt_list.append(str_word_in_front + every_attribute_array[0])
                    str_word_in_front = ''
                    has_number = False
                else:
                    savetxt_list.append(str_word_in_front + every_attribute_array[0])
            # str_word_in_front += every_attribute_array[0]
            # savetxt_list.append(str_word_in_front)
            # str_word_in_front = ''
            # next_is_noun = False
    '''
    save_word_list = []
    for every_attribute_line in every_row:
        every_attribute_array = every_attribute_line.split('\t')
        if len(every_attribute_array) > 3:
            save_word_list.append([every_attribute_array[0].strip(),every_attribute_array[3].strip()])
    length_save_word_list = len(save_word_list)
    for i in range(length_save_word_list-4):
        if i == 0:
            if save_word_list[i][1].find('名詞') != -1 and save_word_list[i][1].find('名詞-数') == -1\
                and save_word_list[i][0] not in MULTIBYTE_MARK:
                savetxt_list.append(save_word_list[i][0])
            elif save_word_list[i][1].find('名詞-数') != -1 and save_word_list[i + 1][1].find('名詞-数') != -1 \
                and save_word_list[i + 2][0] not in MULTIBYTE_MARK and save_word_list[i + 2][1].find('名詞') != -1 \
                and save_word_list[i + 2][1].find('名詞-数') == -1:
                savetxt_list.append(save_word_list[i][0] + save_word_list[i + 1][0] + save_word_list[i + 2][0])
            elif save_word_list[i][1].find('名詞-数') != -1 and save_word_list[i + 1][1].find('名詞-数') != -1 \
                and save_word_list[i + 2][1].find('名詞-数') != -1 and save_word_list[i + 3][0] not in MULTIBYTE_MARK \
                and save_word_list[i + 3][1].find('名詞') != -1 and save_word_list[i + 3][1].find('名詞-数') == -1:
                savetxt_list.append(save_word_list[i][0] + save_word_list[i + 1][0] + save_word_list[i + 2][0])
            elif save_word_list[i][1].find('名詞-数') != -1 and save_word_list[i + 1][0] not in MULTIBYTE_MARK \
                and save_word_list[i + 1][1].find('名詞') != -1 and save_word_list[i + 1][1].find('名詞-数') == -1:
                savetxt_list.append(save_word_list[i][0] + save_word_list[i + 1][0])

        if i>0:
            if save_word_list[i][1].find('名詞') != -1 and save_word_list[i][1].find('名詞-数') == -1 \
                and save_word_list[i-1][1].find('名詞-数') == -1 and save_word_list[i][0] not in MULTIBYTE_MARK:
                savetxt_list.append(save_word_list[i][0])#保存名词
            elif save_word_list[i][1].find('名詞-数') != -1 and save_word_list[i + 1][1].find('名詞-数') != -1 \
                and save_word_list[i + 2][0] not in MULTIBYTE_MARK and save_word_list[i + 2][1].find('名詞') != -1 \
                and save_word_list[i + 2][1].find('名詞-数') == -1 and save_word_list[i-1][1].find('名詞-数') == -1:
                savetxt_list.append(save_word_list[i][0] + save_word_list[i + 1][0] + save_word_list[i + 2][0])#保存数词+数词+名词
            elif save_word_list[i][1].find('名詞-数') != -1 and save_word_list[i + 1][1].find('名詞-数') != -1 \
                and save_word_list[i + 2][1].find('名詞-数') != -1 and save_word_list[i + 3][0] not in MULTIBYTE_MARK\
                and save_word_list[i + 3][1].find('名詞') != -1 and save_word_list[i + 3][1].find('名詞-数') == -1 \
                and save_word_list[i - 1][1].find('名詞-数') == -1:
                savetxt_list.append(save_word_list[i][0] + save_word_list[i + 1][0] + save_word_list[i + 2][0]+save_word_list[i + 3][0])#保存数词+数词+数词+名词
            elif save_word_list[i][1].find('名詞-数') != -1 and save_word_list[i+1][1].find('名詞-数') == -1\
                and save_word_list[i + 1][0] not in MULTIBYTE_MARK and save_word_list[i + 1][1].find('名詞') != -1 \
                and save_word_list[i + 1][1].find('名詞-数') == -1 and save_word_list[i-1][1].find('名詞-数') == -1:
                savetxt_list.append(save_word_list[i][0] + save_word_list[i + 1][0])#保存数词+名词


            elif save_word_list[i][1].find('名詞-数') != -1 and save_word_list[i + 1][1].find('名詞-数') != -1 \
                and save_word_list[i + 2][1].find('名詞') == -1 and save_word_list[i-1][1].find('名詞-数') == -1:
                savetxt_list.append(save_word_list[i][0] + save_word_list[i + 1][0])#保存数词+数词
            elif save_word_list[i][1].find('名詞-数') != -1 and save_word_list[i + 1][1].find('名詞-数') != -1 \
                and save_word_list[i + 2][1].find('名詞-数') != -1 and save_word_list[i + 3][1].find('名詞') == -1\
                and save_word_list[i - 1][1].find('名詞-数') == -1:
                savetxt_list.append(save_word_list[i][0] + save_word_list[i + 1][0] + save_word_list[i + 2][0])#保存数词+数词+数词+数词
            elif save_word_list[i][1].find('名詞-数') != -1 and save_word_list[i+1][1].find('名詞') == -1\
                and save_word_list[i-1][1].find('名詞-数') == -1:
                savetxt_list.append(save_word_list[i][0])#保存数词


    # savetxt_list = [' '.join(i) for i in savetxt_list]  # 不加这一句,重要度就是频率

    new_txt_list = []
    for every_word in savetxt_list:#每个字符都不在特殊符号里并且不是数字的词语添加到new_txt_list
        append_flag = True
        if (every_word is not None and len(every_word.strip()) > 1 and not (every_word.strip().isdigit())):
            for i in every_word:
                if i in MULTIBYTE_MARK:
                    append_flag = False
                    break
            if append_flag == True:
                new_txt_list.append(every_word)

    new_txt_list2 = []
    for every_word in new_txt_list:#不包含no_need_words的词加入到new_txt_list2
        find_flag = False
        for word in no_need_words:
            if every_word.find(word) != -1:
                find_flag = True
                break
        if find_flag == False:
            new_txt_list2.append(every_word)

    new_txt_list3 = []
    for every_word in new_txt_list2:#去掉0和片假名长音'ー'开头的字符串
        find_flag = False
        if not every_word.startswith('0') and not  every_word.startswith('０') and not every_word.startswith('ー'):
            new_txt_list3.append(every_word)
    new_txt_list3 = [' '.join(i) for i in new_txt_list3]#不加这一句,重要度就是频率
    cmp_nouns = new_txt_list3
    return cmp_nouns


def _increase(cmp_nouns, terms):
    """
    専門用語リストへ、整形して追加するサブルーチン
    """
    if len(terms) > 1:
        cmp_noun = ' '.join(terms)
        cmp_nouns.append(cmp_noun)
    del terms[:]


def cmp_noun_dict(data):
    """
    複合語（単名詞の空白区切り）をキーに、その出現回数を値にしたディクショナリを返す
    """
    cmp_noun = cmp_noun_list(data)
    return list2dict(cmp_noun)





def modify_agglutinative_lang(data):
    """
    半角スペースで区切られた単名詞を膠着言語（日本語等）向けに成形する
    """
    data_disp = ""
    eng = 0
    eng_pre = 0
    for noun in data.split(" "):
        if re.match("[A-Z|a-z]+$", noun):
            eng = 1
        else:
            eng = 0
        # 前後ともアルファベットなら半角空白空け、それ以外なら区切りなしで連結
        if eng and eng_pre:
            # data_disp = data_disp + " " + noun
            data_disp = data_disp + noun
        else:
            data_disp = data_disp + noun
        eng_pre = eng
    return data_disp


def score_lr(frequency, ignore_words=None, average_rate=1,
             lr_mode=1, dbm=None):
    """
    専門用語とそれを構成する単名詞の情報から重要度を計算する
        cmp_noun
            複合語（単名詞の空白区切り）をキーに出現回数を値に
            したディクショナリ
        ignore_word
            重要度計算の例外とする語のリスト
        average_rate
            重要度計算においてLRとFrequencyの比重を調整する
            数値が小さいほうがLRの比重が大きい
        lr_mode
            1のときはLRの計算において「延べ数」をとる
            2のときはLRの計算において「異なり数」をとる
    """
    # 対応する関数を呼び出し
    if dbm is None:
        noun_importance = _score_lr_dict(frequency, ignore_words,
                                         average_rate, lr_mode)
    else:
        noun_importance = _score_lr_dbm(frequency, ignore_words,
                                        average_rate, lr_mode, dbm)
    return noun_importance


def _score_lr_dict(frequency, ignore_words, average_rate=1, lr_mode=1):
    # 「専門用語」をキーに、値を「重要度」にしたディクショナリ
    noun_importance = {}
    stat = {}  # 単名詞ごとの連接情報
    # 専門用語ごとにループ
    for cmp_noun in frequency.keys():
        if not cmp_noun:
            continue
        org_nouns = cmp_noun.split(" ")
        nouns = []
        # 数値及び指定の語を重要度計算から除外
        for noun in org_nouns:
            if ignore_words:
                if noun in ignore_words:
                    continue
            elif re.match(r"[\d\.\,]+$", noun):
                continue
            nouns.append(noun)
        # 複合語の場合、連接語の情報をディクショナリに入れる
        if len(nouns) > 1:
            for i in range(0, len(nouns)-1):
                if not nouns[i] in stat:
                    stat[nouns[i]] = [0, 0]
                if not nouns[i+1] in stat:
                    stat[nouns[i+1]] = [0, 0]
                if lr_mode == 1:  # 連接語の”延べ数”をとる場合
                    stat[nouns[i]][0] += frequency[cmp_noun]
                    stat[nouns[i+1]][1] += frequency[cmp_noun]
                elif lr_mode == 2:   # 連接語の”異なり数”をとる場合
                    stat[nouns[i]][0] += 1
                    stat[nouns[i+1]][1] += 1
    for cmp_noun in frequency.keys():
        importance = 1  # 専門用語全体の重要度
        count = 0  # ループカウンター（専門用語中の単名詞数をカウント）
        if re.match(r"\s*$", cmp_noun):
            continue
        for noun in cmp_noun.split(" "):
            if re.match(r"[\d\.\,]+$", noun):
                continue
            left_score = 0
            right_score = 0
            if noun in stat:
                left_score = stat[noun][0]
                right_score = stat[noun][1]
            importance *= (left_score + 1) * (right_score + 1)
            count += 1
        if count == 0:
            count = 1
        # 相乗平均でlr重要度を出す
        importance = importance ** (1 / (2 * average_rate * count))
        noun_importance[cmp_noun] = importance
        count = 0
    return noun_importance


def store_lr(frequency, dbm=None):
    """
    LRの情報をdbmに蓄積する
    """
    stat = dbm  # 単名詞ごとの連接情報
    # 専門用語ごとにループ
    for cmp_noun in frequency.keys():
        if not cmp_noun:
            continue
        nouns = []
        for noun in cmp_noun.split(" "):
            # 数値を重要度計算から除外
            if re.match(r"[\d\.\,]+$", noun):
                continue
            else:
                nouns.append(noun)
        # 複合語の場合、連接語の情報をdbmに入れる
        if len(nouns) > 1:
            for i in range(0, len(nouns)-1):
                if not nouns[i] in stat:
                    stat[nouns[i]] = "\t".join(["0", "0", "0", "0"])
                if not nouns[i+1] in stat:
                    stat[nouns[i+1]] = "\t".join(["0", "0", "0", "0"])
                value_0_pack = stat[nouns[i]].decode("utf-8").split("\t")
                value_0_int = [int(x) for x in value_0_pack]
                value_1_pack = stat[nouns[i+1]].decode("utf-8").split("\t")
                value_1_int = [int(x) for x in value_1_pack]
                # 連接語の”延べ数”をとる場合
                value_0_int[0] += frequency[cmp_noun]
                value_1_int[1] += frequency[cmp_noun]
                # 連接語の”異なり数”をとる場合
                value_0_int[2] += 1
                value_1_int[3] += 1
                # dbmに格納
                value_0 = [str(x) for x in value_0_int]
                value_1 = [str(x) for x in value_1_int]
                stat[nouns[i]] = "\t".join(value_0)
                stat[nouns[i+1]] = "\t".join(value_1)


def _score_lr_dbm(frequency, ignore_words=None, average_rate=1, lr_mode=1,
                  dbm=None):
    """
    dbmに蓄積したLR情報をもとにLRのスコアを出す
    """
    # 「専門用語」をキーに、値を「重要度」にしたディクショナリ
    noun_importance = {}
    stat = dbm    # 単名詞ごとの連接情報
    for cmp_noun in frequency.keys():
        importance = 1       # 専門用語全体の重要度
        count = 0     # 専門用語中の単名詞数をカウント
        if re.match(r"\s*$", cmp_noun):
            continue
        for noun in cmp_noun.split(" "):
            if re.match(r"[\d\.\,]+$", noun):
                continue
            left_score = 0
            right_score = 0
            if noun in stat:
                value = stat[noun].decode("utf-8").split("\t")
                if lr_mode == 1:  # 連接語の”延べ数”をとる場合
                    left_score = int(value[0])
                    right_score = int(value[1])
                elif lr_mode == 2:  # 連接語の”異なり数”をとる場合
                    left_score = int(value[3])
                    right_score = int(value[4])
            if noun not in ignore_words and not re.match(r"[\d\.\,]+$", noun):
                importance *= (left_score + 1) * (right_score + 1)
                count += 1
        if count == 0:
            count = 1
        # 相乗平均でLR重要度を出す
        importance = importance ** (1 / (2 * average_rate * count))
        noun_importance[cmp_noun] = importance
        count = 0
    return noun_importance


def term_importance(*args):
    """
    複数のディクショナリの値同士を乗算する
    """
    master = {}
    new_master = {}
    for noun_dict in args:
        for nouns, importance in noun_dict.items():
            if nouns in master:
                new_master[nouns] = master[nouns] * importance
            else:
                new_master[nouns] = importance
        master = new_master.copy()
    return master


def frequency2tf(frequency):
    """
    Frequencyの情報をもとにTFを作成する
    """
    tf_score = frequency.copy()
    tf_data = {}
    # 単名詞数ごとのリストを作る
    for cmp_noun in frequency.keys():
        if re.match(r"^\s*$", cmp_noun):
            continue
        nouns = cmp_noun.split(" ")
        length_of_nouns = len(nouns)
        if length_of_nouns not in tf_data:
            tf_data[length_of_nouns] = []
        else:
            tf_data[length_of_nouns].append(cmp_noun)
    # 短い語からループさせる
    length_list1 = sorted(tf_data.keys(), key=int)
    length_list2 = length_list1.copy()
    del length_list1[-1]
    del length_list2[0]
    for len1 in length_list1:
        for nouns1 in tf_data[len1]:
            nouns1_work = " " + nouns1 + " "
            for len2 in length_list2:
                for nouns2 in tf_data[len2]:
                    nouns2_work = " " + nouns2 + " "
                    if nouns1_work in nouns2_work:
                        tf_score[nouns1] += frequency[nouns2]
        del length_list2[0]
    return tf_score


def store_df(cmp_nouns, dbm=None):
    """
    DF (Document Frequency)の情報を蓄積する
    """
    # トータル文書数情報がないときは初期化
    if TOTAL_MARK not in dbm:
        dbm[TOTAL_MARK] = "0"
    # データを一回読み込むごとに、文書数+1
    total = int(dbm[TOTAL_MARK].decode("utf-8"))
    new_total = str(total + 1)
    dbm[TOTAL_MARK] = new_total
    # 専門用語ごとにループ
    for cmp_noun in cmp_nouns.keys():
        if not cmp_noun:
            continue
        if cmp_noun == TOTAL_MARK:
            continue
        if cmp_noun in dbm:
            count = int(dbm[cmp_noun].decode("utf-8"))
            new_count = str(count + 1)
            dbm[cmp_noun] = new_count
        else:
            dbm[cmp_noun] = "1"


def get_idf(cmp_nouns, dbm=None):
    """
    蓄積したDFの情報をもとにIDFを返す
    """
    idf_score = {}
    total = int(dbm[TOTAL_MARK].decode("utf-8"))
    # 専門用語ごとにループ
    for cmp_noun in cmp_nouns.keys():
        if not cmp_noun:
            continue
        if cmp_noun in dbm:
            count = int(dbm[cmp_noun].decode("utf-8"))
            if count != 0:
                idf_score[cmp_noun] = total / count
    return idf_score


def list2dict(list_data):
    """
    リストの要素をキーに、その出現回数を値にしたディクショナリを返す
    """
    dict_data = {}
    for data in list_data:
        if data in dict_data:
            dict_data[data] += 1
        else:
            dict_data[data] = 1
    return dict_data


# 複合語を抽出し、重要度を算出
frequency = cmp_noun_dict(text)
LR = score_lr(frequency,
         ignore_words=IGNORE_WORDS,
         lr_mode=1, average_rate=1
     )
term_imp = term_importance(frequency, LR)

# 重要度が高い順に並べ替えて出力
data_collection = collections.Counter(term_imp)
for cmp_noun, value in data_collection.most_common():
    print(modify_agglutinative_lang(cmp_noun), value, sep="\t")
