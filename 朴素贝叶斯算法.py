import math
import sys
import MeCab
import csv

no_need_words = ["これ","ここ","こと","それ","ため","よう","さん","そこ","たち","ところ","それぞれ","これら","どれ","br"]

MULTIBYTE_MARK = set([
    '、', ',', '，', '。', '．','\'', '”', '“', '《', '》', '：', '（', '）', '(', ')', '；', '.', '・', '～', '`',
    '%', '％', '$', '￥', '~', '■', '●', '◆', '×', '※', '►', '▲', '▼', '‣', '·', '∶', ':', '‐', '_', '‼', '≫',
    '－','−', ';', '･', '〈', '〉', '「', '」', '『', '』', '【', '】', '〔', '〕', '?', '？', '!', '！', '+', '-',
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


class NaiveBayes():
    def __init__(self):
        self.vocabularies = set()
        self.word_count = {}
        self.category_count = {}

    def to_words(self, sentence):
        """
        入力: 'すべて自分のほうへ'
        出力: tuple(['すべて', '自分', 'の', 'ほう', 'へ'])
        """
        savetxt_list = []
        mecab = MeCab.Tagger("-Ochasen")  # 有词性标注的
        # mecab = MeCab.Tagger("-Owakati")  # 没有词性标注的
        # data = data.replace("<br/>", "")
        # data = data.replace("<br>", "")
        cmp_nouns = mecab.parse(sentence)
        every_row = cmp_nouns.split('\n')
        save_word_list = []
        for every_attribute_line in every_row:
            every_attribute_array = every_attribute_line.split('\t')
            if len(every_attribute_array) > 3:
                save_word_list.append([every_attribute_array[0].strip(), every_attribute_array[3].strip()])
        length_save_word_list = len(save_word_list)
        for i in range(length_save_word_list - 4):
            if i == 0:
                if save_word_list[i][1].find('名詞') != -1 and save_word_list[i][1].find('名詞-数') == -1 \
                        and save_word_list[i][0] not in MULTIBYTE_MARK:
                    savetxt_list.append(save_word_list[i][0])
                elif save_word_list[i][1].find('名詞-数') != -1 and save_word_list[i + 1][1].find('名詞-数') != -1 \
                        and save_word_list[i + 2][0] not in MULTIBYTE_MARK and save_word_list[i + 2][1].find('名詞') != -1 \
                        and save_word_list[i + 2][1].find('名詞-数') == -1:
                    savetxt_list.append(save_word_list[i][0] + save_word_list[i + 1][0] + save_word_list[i + 2][0])
                elif save_word_list[i][1].find('名詞-数') != -1 and save_word_list[i + 1][1].find('名詞-数') != -1 \
                        and save_word_list[i + 2][1].find('名詞-数') != -1 and save_word_list[i + 3][
                    0] not in MULTIBYTE_MARK \
                        and save_word_list[i + 3][1].find('名詞') != -1 and save_word_list[i + 3][1].find('名詞-数') == -1:
                    savetxt_list.append(save_word_list[i][0] + save_word_list[i + 1][0] + save_word_list[i + 2][0])
                elif save_word_list[i][1].find('名詞-数') != -1 and save_word_list[i + 1][0] not in MULTIBYTE_MARK \
                        and save_word_list[i + 1][1].find('名詞') != -1 and save_word_list[i + 1][1].find('名詞-数') == -1:
                    savetxt_list.append(save_word_list[i][0] + save_word_list[i + 1][0])

            if i > 0:
                if save_word_list[i][1].find('名詞') != -1 and save_word_list[i][1].find('名詞-数') == -1 \
                        and save_word_list[i - 1][1].find('名詞-数') == -1 and save_word_list[i][0] not in MULTIBYTE_MARK:
                    savetxt_list.append(save_word_list[i][0])  # 保存名词
                elif save_word_list[i][1].find('名詞-数') != -1 and save_word_list[i + 1][1].find('名詞-数') != -1 \
                        and save_word_list[i + 2][0] not in MULTIBYTE_MARK and save_word_list[i + 2][1].find('名詞') != -1 \
                        and save_word_list[i + 2][1].find('名詞-数') == -1 and save_word_list[i - 1][1].find('名詞-数') == -1:
                    savetxt_list.append(
                        save_word_list[i][0] + save_word_list[i + 1][0] + save_word_list[i + 2][0])  # 保存数词+数词+名词
                elif save_word_list[i][1].find('名詞-数') != -1 and save_word_list[i + 1][1].find('名詞-数') != -1 \
                        and save_word_list[i + 2][1].find('名詞-数') != -1 and save_word_list[i + 3][
                    0] not in MULTIBYTE_MARK \
                        and save_word_list[i + 3][1].find('名詞') != -1 and save_word_list[i + 3][1].find('名詞-数') == -1 \
                        and save_word_list[i - 1][1].find('名詞-数') == -1:
                    savetxt_list.append(save_word_list[i][0] + save_word_list[i + 1][0] + save_word_list[i + 2][0] +
                                        save_word_list[i + 3][0])  # 保存数词+数词+数词+名词
                elif save_word_list[i][1].find('名詞-数') != -1 and save_word_list[i + 1][1].find('名詞-数') == -1 \
                        and save_word_list[i + 1][0] not in MULTIBYTE_MARK and save_word_list[i + 1][1].find('名詞') != -1 \
                        and save_word_list[i + 1][1].find('名詞-数') == -1 and save_word_list[i - 1][1].find('名詞-数') == -1:
                    savetxt_list.append(save_word_list[i][0] + save_word_list[i + 1][0])  # 保存数词+名词

                '''
                #保存数词
                elif save_word_list[i][1].find('名詞-数') != -1 and save_word_list[i + 1][1].find('名詞-数') != -1 \
                    and save_word_list[i + 2][1].find('名詞') == -1 and save_word_list[i-1][1].find('名詞-数') == -1:
                    savetxt_list.append(save_word_list[i][0] + save_word_list[i + 1][0])#保存数词+数词
                elif save_word_list[i][1].find('名詞-数') != -1 and save_word_list[i + 1][1].find('名詞-数') != -1 \
                    and save_word_list[i + 2][1].find('名詞-数') != -1 and save_word_list[i + 3][1].find('名詞') == -1\
                    and save_word_list[i - 1][1].find('名詞-数') == -1:
                    savetxt_list.append(save_word_list[i][0] + save_word_list[i + 1][0] + save_word_list[i + 2][0])#保存数词+数词+数词
                elif save_word_list[i][1].find('名詞-数') != -1 and save_word_list[i+1][1].find('名詞') == -1\
                    and save_word_list[i-1][1].find('名詞-数') == -1:
                    savetxt_list.append(save_word_list[i][0])#保存数词
                '''

        new_txt_list = []
        for every_word in savetxt_list:  # 每个字符都不在特殊符号里并且不是数字的词语添加到new_txt_list
            append_flag = True
            if (every_word is not None and len(every_word.strip()) > 1 and not (every_word.strip().isdigit())):
                for i in every_word:
                    if i in MULTIBYTE_MARK:
                        append_flag = False
                        break
                if append_flag == True:
                    new_txt_list.append(every_word)

        new_txt_list2 = []
        for every_word in new_txt_list:  # 不包含no_need_words的词加入到new_txt_list2
            find_flag = False
            for word in no_need_words:
                if every_word.find(word) != -1:
                    find_flag = True
                    break
            if find_flag == False:
                new_txt_list2.append(every_word)

        new_txt_list3 = []
        for every_word in new_txt_list2:  # 去掉0和片假名长音'ー'开头的字符串
            if not every_word.startswith('0') and not every_word.startswith('０') and not every_word.startswith('ー'):
                new_txt_list3.append(every_word)
        # new_txt_list3 = [' '.join(i) for i in new_txt_list3]
        cmp_nouns = new_txt_list3
        return tuple(cmp_nouns)

    def word_count_up(self, word, category):
        self.word_count.setdefault(category, {})
        self.word_count[category].setdefault(word, 0)
        self.word_count[category][word] += 1
        self.vocabularies.add(word)

    def category_count_up(self, category):
        self.category_count.setdefault(category, 0)
        self.category_count[category] += 1

    def train(self, doc, category):
        words = self.to_words(doc)
        for word in words:
            self.word_count_up(word, category)
        self.category_count_up(category)

    def prior_prob(self, category):
        num_of_categories = sum(self.category_count.values())
        num_of_docs_of_the_category = self.category_count[category]
        return num_of_docs_of_the_category / num_of_categories

    def num_of_appearance(self, word, category):
        if word in self.word_count[category]:
            return self.word_count[category][word]
        return 0

    def word_prob(self, word, category):
        # ベイズの法則の計算。通常、非常に0に近い小数になる。
        numerator = self.num_of_appearance(word, category) + 1  # +1は加算スムージングのラプラス法
        denominator = sum(self.word_count[category].values()) + len(self.vocabularies)
        # Python3では、割り算は自動的にfloatになる
        prob = numerator / denominator
        return prob

    def score(self, words, category):
        # logを取るのは、word_probが0.000....01くらいの小数になったりするため
        score = math.log(self.prior_prob(category))
        for word in words:
            score += math.log(self.word_prob(word, category))
        return score

    # logを取らないと値が小さすぎてunderflowするかも。
    def score_without_log(self, words, category):
        score = self.prior_prob(category)
        for word in words:
            score *= self.word_prob(word, category)
        return score

    def classify(self, doc):
        best_guessed_category = None
        max_prob_before = -sys.maxsize
        words = self.to_words(doc)
        for category in self.category_count.keys():
            prob = self.score(words, category)
            if prob > max_prob_before:
                max_prob_before = prob
                best_guessed_category = category
        return best_guessed_category


    def read_top_from_csv(self,csv_path):
        csvFile = open(csv_path, "r")
        reader = csv.reader(csvFile)
        toplist = []
        for item in reader:
            # if reader.line_num == 1:
            #     continue
            toplist.append(item)
        return toplist



if __name__ == '__main__':
    
    csv_file = r'D:/19teacher.csv'
    nb = NaiveBayes()
    top_list = nb.read_top_from_csv(csv_file)
    for row in top_list:
        nb.train(row[1],row[2])
    doc = ''
    with open(r'D:/3.txt', 'r', encoding='utf-8') as f:
        doc = f.read()
    employee_keywords_list = list(nb.to_words(doc))
    print('推定カテゴリ: %s' % (nb.classify(doc)))  # 推定カテゴリ: Pythonになるはず
    print('Aカテゴリである確率: %s' % nb.score_without_log(employee_keywords_list, 'A'))
    print('Bカテゴリである確率: %s' % nb.score_without_log(employee_keywords_list, 'B'))
    





