# -*- coding: UTF-8 -*-
import MeCab
import re
import collections
import pymssql
import datetime
import time
import logging
import os
import configparser
import xlwt
import xlrd
from xlutils.copy import copy
import decimal #不加打包成exe会出错



IGNORE_WORDS = set([])  # 重要度計算外とする語
no_need_words = ["これ","ここ","こと","それ","ため","よう","さん","そこ","たち","ところ","それぞれ","これら","どれ","br"]
# ひらがな
JP_HIRA = set([chr(i) for i in range(12353, 12436)])
# カタカナ
JP_KATA = set([chr(i) for i in range(12449, 12532+1)])
#要忽略的字符
# "ー"特殊
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
        if not morph:
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
                _increase(cmp_nouns, terms)
                is_stopword = 1
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
                is_kata = 1
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
                savetxt_list.append(save_word_list[i][0])#保存名词
            elif save_word_list[i][1].find('名詞-数') != -1 and save_word_list[i + 1][1].find('名詞-数') != -1 \
                and save_word_list[i + 2][0] not in MULTIBYTE_MARK and save_word_list[i + 2][1].find('名詞') != -1 \
                and save_word_list[i + 2][1].find('名詞-数') == -1:
                savetxt_list.append(save_word_list[i][0] + save_word_list[i + 1][0] + save_word_list[i + 2][0])#保存数词+数词+名词
            elif save_word_list[i][1].find('名詞-数') != -1 and save_word_list[i + 1][1].find('名詞-数') != -1 \
                and save_word_list[i + 2][1].find('名詞-数') != -1 and save_word_list[i + 3][0] not in MULTIBYTE_MARK \
                and save_word_list[i + 3][1].find('名詞') != -1 and save_word_list[i + 3][1].find('名詞-数') == -1:
                savetxt_list.append(save_word_list[i][0] + save_word_list[i + 1][0] + save_word_list[i + 2][0] + save_word_list[i + 3][0])#保存数词+数词+数词+名词
            elif save_word_list[i][1].find('名詞-数') != -1 and save_word_list[i + 1][0] not in MULTIBYTE_MARK \
                and save_word_list[i + 1][1].find('名詞') != -1 and save_word_list[i + 1][1].find('名詞-数') == -1:
                savetxt_list.append(save_word_list[i][0] + save_word_list[i + 1][0])#保存数词+名词

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


def score_lr(frequency, ignore_words=None, average_rate=1, lr_mode=1, dbm=None):
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
        noun_importance = _score_lr_dict(frequency, ignore_words, average_rate, lr_mode)
    else:
        noun_importance = _score_lr_dbm(frequency, ignore_words, average_rate, lr_mode, dbm)
    return noun_importance


def _score_lr_dbm(frequency, ignore_words=None, average_rate=1, lr_mode=1, dbm=None):
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

'''
def calculate_importance(member_txt):
    tatext_member = member_txt
    content = re.sub('\s', '', member_txt)#去掉空白字符
    length_member_topReport_content = len(content)
    # 複合語を抽出し、重要度を算出
    frequency_member = cmp_noun_dict(tatext_member)
    LR_member = score_lr(frequency_member, ignore_words=IGNORE_WORDS, lr_mode=1, average_rate=1)
    term_imp_member = term_importance(frequency_member, LR_member)
    # 重要度が高い順に並べ替えて出力
    data_collection_member = collections.Counter(term_imp_member)
    totalImportance_member = 0
    # key_words_lenth_member = len(data_collection_member)
    key_words_list_memeber = []
    for cmp_noun, value in data_collection_member.most_common():
        totalImportance_member += value
        key_words_list_memeber.append(cmp_noun)
    return totalImportance_member,length_member_topReport_content
'''

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

def calculate_importance_to_excel(member_txt,year,week,employee_code,file_path):
    '''
    :param member_txt: 文章
    :param year: top报告年份
    :param week: top报告周
    :param employee_code: 社员号
    '''
    rexcel = xlrd.open_workbook(file_path)  # 用wlrd提供的方法读取一个excel文件
    rows = rexcel.sheets()[0].nrows  # 用wlrd提供的方法获得现在已有的行数
    excel = copy(rexcel)  # 用xlutils提供的copy方法将xlrd的对象转化为xlwt的对象
    worksheet = excel.get_sheet(0)  # 用xlwt对象的方法获得要操作的sheet
    current_row = rows
    tatext_member = member_txt
    content = re.sub('\s', '', member_txt)#去掉空白字符
    length_member_topReport_content = len(content)
    # 複合語を抽出し、重要度を算出
    frequency_member = cmp_noun_dict(tatext_member)
    LR_member = score_lr(frequency_member, ignore_words=IGNORE_WORDS, lr_mode=1, average_rate=1)
    term_imp_member = term_importance(frequency_member, LR_member)
    # 重要度が高い順に並べ替えて出力
    data_collection_member = collections.Counter(term_imp_member)
    totalImportance_member = 0
    # key_words_lenth_member = len(data_collection_member)
    key_words_list_memeber = []
    for cmp_noun, value in data_collection_member.most_common():
        worksheet.write(current_row, 0, label=year)
        worksheet.write(current_row, 1, label=week)
        worksheet.write(current_row, 2, label=employee_code)
        worksheet.write(current_row, 3, label=cmp_noun)
        worksheet.write(current_row, 4, label=value)
        current_row += 1
        totalImportance_member += value
        key_words_list_memeber.append(cmp_noun)
    excel.save(file_path)


def get_year_week_from_Mst_date(server, user, password, database, current_date):
    '''
    :param server:服务器名称
    :param user:用户名
    :param password:密码
    :param database:数据库名
    :param current_date:系统当前日期年-月-日
    :return:Mst_date表返回的当前年和当前周
    '''
    try:
        conn = pymssql.connect(server, user, password, database)
        cur = conn.cursor()
        sql = " select year_no,week_no from Mst_date where date_mst='%s' "  % current_date
        cur.execute(sql)
        rows = cur.fetchall()
        if rows != []:
            current_year = rows[0][0]
            current_week = rows[0][1]
            return current_year,current_week
        else:
            return ""
    except pymssql.Error as ex:
        logger.error("dbException:" + str(ex))
        raise ex
    except Exception as ex:
        logger.error("Call method get_year_week_from_Mst_date() error!Can not query from table Mst_date!")
        logger.error("Exception:" + str(ex))
        raise ex
    finally:
        conn.close()


def read_dateConfig_file_set_database():
    if os.path.exists(os.path.join(os.path.dirname(__file__), "dateConfig.ini")):
        try:
            conf = configparser.ConfigParser()
            conf.read(os.path.join(os.path.dirname(__file__), "dateConfig.ini"), encoding="utf-8-sig")
            server = conf.get("server", "server")
            user = conf.get("user", "user")
            password = conf.get("password", "password")
            database = conf.get("database", "database")
            return server,user,password,database
        except Exception as ex:
            logger.error("Content in dateConfig.ini about database has error.")
            logger.error("Exception:" + str(ex))
            raise ex


def read_dateConfig_file_set_year_week():
    global report_year
    global report_week
    if os.path.exists(os.path.join(os.path.dirname(__file__), "dateConfig.ini")):
        try:
            conf = configparser.ConfigParser()
            conf.read(os.path.join(os.path.dirname(__file__), "dateConfig.ini"), encoding="utf-8-sig")
            year = conf.get("execute_year", "year")
            week = conf.get("execute_week", "week")
            if  year:
                report_year = year
            if week:
                report_week = week
        except Exception as ex:
            logger.error("Content in dateConfig.ini about execute_year or execute_week has error.")
            logger.error("Exception:" + str(ex))
            raise ex


def get_employee_list_from_table_report_target(server, user, password, database):
    '''
    :param server: 服务器名称
    :param user:用户名
    :param password:密码
    :param database:数据库名
    :return:report_target表去重后的社员号列表
    '''
    try:
        conn = pymssql.connect(server, user, password, database)
        cur = conn.cursor()
        sql = " select distinct cast(employee_code as int) as employee_code from report_target order by employee_code "
        cur.execute(sql)
        rows = cur.fetchall()
        if rows:
            employee_list = []
            for row in rows:
                employee_list.append(list(row))
            return employee_list
        else:
            return ""
    except pymssql.Error as ex:
        logger.error("dbException:" + str(ex))
        raise ex
    except Exception as ex:
        logger.error("Call method get_employee_list_from_table_report_target() error!Can not query from table report_target!")
        logger.error("Exception:"+str(ex))
        raise ex
    finally:
        conn.close()


def read_report_from_database(server, user, password, database,report_year,report_week,employee_code):
    '''
    :param server:服务器名称
    :param user:用户名
    :param password:密码
    :param database:数据库名
    :param report_year:top报告年份
    :param report_week:top报告周
    :param employee_code:社员号
    :return:top报告内容
    '''
    try:
        conn = pymssql.connect(server, user, password, database)
        cur = conn.cursor()
        sql = "select remark from report where report_year =%s and report_week =%s and employee_code =%s" \
              % (report_year, report_week, employee_code)
        cur.execute(sql)
        rows = cur.fetchall()
        if rows:
            content = rows[0][0]
            return content
        else:
            return ""
    except pymssql.Error as ex:
        logger.error("dbException:" + str(ex))
        raise ex
    except Exception as ex:
        logger.error("Call method read_report_from_database() error!Can not query from table report!")
        logger.error("Exception:" + str(ex))
        raise ex
    finally:
        conn.close()


def calculate_importance_of_everyword_output_to_excel(server, user, password, database, employee_list, report_year, report_week):
    '''
    :param employee_list:report_target表的社员列表
    :param report_year:top报告年份
    :param report_week_list:top报告周
    '''
    try:
        myweek = report_week
        if int(myweek) <10:
            myweek = '0'+myweek
        fileName = report_year + myweek + '.xls'
        workbook = xlwt.Workbook(encoding='UTF-8')
        worksheet = workbook.add_sheet('重要度')
        worksheet.write(0, 0, label='年')
        worksheet.write(0, 1, label='週')
        worksheet.write(0, 2, label='社員CD')
        worksheet.write(0, 3, label='キーワード')
        worksheet.write(0, 4, label='重要度')
        savePath = r'D:/' + fileName
        workbook.save(savePath)
        if employee_list:
            for employee in employee_list:
                employee_report = read_report_from_database(server, user, password, database, report_year,report_week,employee)# 社员TOP报告内容
                if employee_report:#top报告有内容采取向excel输出信息
                    rexcel = xlrd.open_workbook(savePath)  # 用wlrd提供的方法读取一个excel文件
                    rows = rexcel.sheets()[0].nrows  # 用wlrd提供的方法获得现在已有的行数
                    excel = copy(rexcel)  # 用xlutils提供的copy方法将xlrd的对象转化为xlwt的对象
                    worksheet = excel.get_sheet(0)  # 用xlwt对象的方法获得要操作的sheet
                    current_row = rows
                    # content = re.sub('\s', '', employee_report)#去掉空白字符
                    # 複合語を抽出し、重要度を算出
                    frequency_member = cmp_noun_dict(employee_report)
                    LR_member = score_lr(frequency_member, ignore_words=IGNORE_WORDS, lr_mode=1, average_rate=1)
                    term_imp_member = term_importance(frequency_member, LR_member)
                    # 重要度が高い順に並べ替えて出力
                    data_collection_member = collections.Counter(term_imp_member)
                    totalImportance_member = 0
                    # key_words_lenth_member = len(data_collection_member)
                    key_words_list_memeber = []
                    for cmp_noun, value in data_collection_member.most_common():
                        worksheet.write(current_row, 0, label=report_year)
                        worksheet.write(current_row, 1, label=report_week)
                        worksheet.write(current_row, 2, label=employee)
                        worksheet.write(current_row, 3, label=modify_agglutinative_lang(cmp_noun))
                        worksheet.write(current_row, 4, label=value)
                        current_row += 1
                        totalImportance_member += value
                        key_words_list_memeber.append(cmp_noun)
                    excel.save(savePath)

    except pymssql.Error as ex:
        logger.error("dbException:" + str(ex))
        raise ex
    except Exception as ex:
        logger.error("Call method calculate_importance_of_everyword_output_to_excel() error!There is a null value in the parameters.!")
        logger.error("Exception:" + str(ex))
        raise ex


def write_log():
    '''
    :return: 返回logger对象
    '''
    # 获取logger实例，如果参数为空则返回root logger
    logger = logging.getLogger()
    now_date = datetime.datetime.now().strftime('%Y%m%d')
    log_file = now_date+".log"# 文件日志
    if not os.path.exists("log"):#python文件同级别创建log文件夹
        os.makedirs("log")
    # 指定logger输出格式
    formatter = logging.Formatter('%(asctime)s %(levelname)s line:%(lineno)s %(message)s')
    file_handler = logging.FileHandler("log" + os.sep + log_file, mode='a', encoding='utf-8')
    file_handler.setFormatter(formatter) # 可以通过setFormatter指定输出格式
    # 为logger添加的日志处理器，可以自定义日志处理器让其输出到其他地方
    logger.addHandler(file_handler)
    # 指定日志的最低输出级别，默认为WARN级别
    logger.setLevel(logging.INFO)
    return logger


if __name__=="__main__":
    logger = write_log()  # 获取日志对象
    time_start = datetime.datetime.now()
    start = time.clock()
    logger.info("Program start,now time is:"+str(time_start))
    server,user,password,database = read_dateConfig_file_set_database()#读取配置文件中的数据库信息
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")#系统当前日期
    current_year,current_week = get_year_week_from_Mst_date(server, user, password, database, current_date)#从Mst_date获取当前年和周
    report_year = str(current_year)#当前系统年
    report_week = str(current_week) #当前系统周
    read_dateConfig_file_set_year_week()#读配置文件设置report_year和report_week
    logger.info("report_year:" + report_year)
    logger.info("report_week:" + report_week)
    employee_list=[5, 33]
    employee_list =[str(i) for i in employee_list]
    calculate_importance_of_everyword_output_to_excel(server, user, password, database, employee_list, report_year, report_week)#生成关键字和重要度写入Excel
    time_end = datetime.datetime.now()
    end = time.clock()
    logger.info("Program end,now time is:"+str(time_end))
    logger.info("Program run : %f seconds" % (end - start))

