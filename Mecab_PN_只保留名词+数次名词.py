# -*- coding: UTF-8 -*-
import re
import csv
import time
import pandas as pd
import matplotlib.pyplot as plt
import MeCab
import random
import numpy as np
import csv
import pymssql


'''
http://www.statsbeginner.net/entry/2017/05/07/091435
#这个网页的代码坑很多
'''

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


def get_top_list(server, user, password, database):
    try:
        conn = pymssql.connect(server, user, password, database)
        cur = conn.cursor()
        sql = " select convert(int,employee_code) as employee_code,report_year,report_week,remark from report " \
              " where report_year=2018 and report_week between 1 and 26 and  employee_code in (10023844) " \
              " order by employee_code,report_year,report_week "
        cur.execute(sql)
        rows = cur.fetchall()
        if rows :
            top_list = []
            for top in rows:
                top_list.append(list(top))
            return top_list
        else:
            return ""
    except pymssql.Error as ex:
        raise ex
    except Exception as ex:
        raise ex
    finally:
        conn.close()


'''
def get_diclist(text):
    parsed = m.parse(text)      # 形態素解析結果（改行を含む文字列として得られる）
    lines = parsed.split('\n')  # 解析結果を1行（1語）ごとに分けてリストにする
    lines = lines[0:-2]         # 後ろ2行は不要なので削除
    diclist = []
    for word in lines:
        l = re.split('\t|,',word)  # 各行はタブとカンマで区切られてるので
        d = {'Surface':l[0], 'POS1':l[1], 'POS2':l[2], 'BaseForm':l[7]}
        diclist.append(d)
    return(diclist)
'''


def get_diclist(text):
    """
    和文テキストを受け取り、複合語（空白区切りの単名詞）のリストを返す
    """
    savetxt_list = []
    mecab = MeCab.Tagger("-Ochasen")  # 有词性标注的
    cmp_nouns = mecab.parse(text)
    every_row = cmp_nouns.split('\n')
    save_word_list = []
    for every_attribute_line in every_row:
        every_attribute_array = every_attribute_line.split('\t')
        if len(every_attribute_array) > 3:
            save_word_list.append([every_attribute_array[0].strip(), every_attribute_array[3].strip(),every_attribute_array[2].strip()])#every_attribute_array[2]は語の辞書形
    length_save_word_list = len(save_word_list)
    for i in range(length_save_word_list - 4):
        if i == 0:
            if save_word_list[i][1].find('名詞') != -1 and save_word_list[i][1].find('名詞-数') == -1 \
                    and save_word_list[i][0] not in MULTIBYTE_MARK:
                savetxt_list.append([save_word_list[i][0],save_word_list[i][2]])  # 保存名词,字典形
            elif save_word_list[i][1].find('名詞-数') != -1 and save_word_list[i + 1][1].find('名詞-数') != -1 \
                    and save_word_list[i + 2][0] not in MULTIBYTE_MARK and save_word_list[i + 2][1].find('名詞') != -1 \
                    and save_word_list[i + 2][1].find('名詞-数') == -1:
                savetxt_list.append(
                    [save_word_list[i][0] + save_word_list[i + 1][0] + save_word_list[i + 2][0],save_word_list[i][2]+save_word_list[i + 1][2]+save_word_list[i + 2][2]])  # 保存数词+数词+名词,字典形
            elif save_word_list[i][1].find('名詞-数') != -1 and save_word_list[i + 1][1].find('名詞-数') != -1 \
                    and save_word_list[i + 2][1].find('名詞-数') != -1 and save_word_list[i + 3][0] not in MULTIBYTE_MARK \
                    and save_word_list[i + 3][1].find('名詞') != -1 and save_word_list[i + 3][1].find('名詞-数') == -1:
                savetxt_list.append(
                    [save_word_list[i][0] + save_word_list[i + 1][0] + save_word_list[i + 2][0] + save_word_list[i + 3][0], save_word_list[i][2] + save_word_list[i + 1][2] + save_word_list[i + 2][2] + save_word_list[i + 3][2]])  # 保存数词+数词+数词+名词,字典形
            elif save_word_list[i][1].find('名詞-数') != -1 and save_word_list[i + 1][0] not in MULTIBYTE_MARK \
                    and save_word_list[i + 1][1].find('名詞') != -1 and save_word_list[i + 1][1].find('名詞-数') == -1:
                savetxt_list.append([save_word_list[i][0] + save_word_list[i + 1][0], save_word_list[i][2] + save_word_list[i + 1][2]])  # 保存数词+名词,字典形

        if i > 0:
            if save_word_list[i][1].find('名詞') != -1 and save_word_list[i][1].find('名詞-数') == -1 \
                    and save_word_list[i - 1][1].find('名詞-数') == -1 and save_word_list[i][0] not in MULTIBYTE_MARK:
                savetxt_list.append([save_word_list[i][0], save_word_list[i][2]])  # 保存名词,字典形
            elif save_word_list[i][1].find('名詞-数') != -1 and save_word_list[i + 1][1].find('名詞-数') != -1 \
                    and save_word_list[i + 2][0] not in MULTIBYTE_MARK and save_word_list[i + 2][1].find('名詞') != -1 \
                    and save_word_list[i + 2][1].find('名詞-数') == -1 and save_word_list[i - 1][1].find('名詞-数') == -1:
                savetxt_list.append(
                    [save_word_list[i][0] + save_word_list[i + 1][0] + save_word_list[i + 2][0], save_word_list[i][2] + save_word_list[i + 1][2] + save_word_list[i + 2][2]])  # 保存数词+数词+名词,字典形
            elif save_word_list[i][1].find('名詞-数') != -1 and save_word_list[i + 1][1].find('名詞-数') != -1 \
                    and save_word_list[i + 2][1].find('名詞-数') != -1 and save_word_list[i + 3][0] not in MULTIBYTE_MARK \
                    and save_word_list[i + 3][1].find('名詞') != -1 and save_word_list[i + 3][1].find('名詞-数') == -1 \
                    and save_word_list[i - 1][1].find('名詞-数') == -1:
                savetxt_list.append(
                    [save_word_list[i][0] + save_word_list[i + 1][0] + save_word_list[i + 2][0] + save_word_list[i + 3][0], save_word_list[i][2] + save_word_list[i + 1][2] + save_word_list[i + 2][2] + save_word_list[i + 3][2]])  # 保存数词+数词+数词+名词,字典形
            elif save_word_list[i][1].find('名詞-数') != -1 and save_word_list[i + 1][1].find('名詞-数') == -1 \
                    and save_word_list[i + 1][0] not in MULTIBYTE_MARK and save_word_list[i + 1][1].find('名詞') != -1 \
                    and save_word_list[i + 1][1].find('名詞-数') == -1 and save_word_list[i - 1][1].find('名詞-数') == -1:
                savetxt_list.append([save_word_list[i][0] + save_word_list[i + 1][0], save_word_list[i][2] + save_word_list[i + 1][2]])  # 保存数词+名词,字典形

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
    for every_word in savetxt_list:  # 每个字符都不在特殊符号里并且不是数字的词语添加到new_txt_list
        append_flag = True
        if (every_word[0] is not None and len(every_word[0].strip()) > 1 and not (every_word[0].strip().isdigit())):
            for i in every_word[0]:
                if i in MULTIBYTE_MARK:
                    append_flag = False
                    break
            if append_flag == True:
                new_txt_list.append(every_word)

    new_txt_list2 = []
    for every_word in new_txt_list:  # 不包含no_need_words的词加入到new_txt_list2
        find_flag = False
        for word in no_need_words:
            if every_word[0].find(word) != -1:
                find_flag = True
                break
        if find_flag == False:
            new_txt_list2.append(every_word)

    new_txt_list3 = []
    for every_word in new_txt_list2:  # 去掉0和片假名长音'ー'开头的字符串
        if not every_word[0].startswith('0') and not every_word[0].startswith('０') and not every_word[0].startswith('ー'):
            new_txt_list3.append(every_word)
    cmp_nouns = new_txt_list3

    diclist = []
    for word in cmp_nouns:
        d = {'Surface':word[0], 'BaseForm':word[1]}
        diclist.append(d)
    return diclist


# 形態素解析結果の単語ごとdictデータにPN値を追加する関数
def add_pnvalue(diclist_old):
    diclist_new = []
    for word in diclist_old:
        base = word['BaseForm']        # 個々の辞書から基本形を取得
        if base in pn_dict:
            pn = float(pn_dict[base])  # 中身の型があれなので
        else:
            pn = 'notfound'            # その語がPN Tableになかった場合
        word['PN'] = pn
        diclist_new.append(word)
    return diclist_new


def get_pnmean(diclist):
    pn_list = []
    for word in diclist:
        pn = word['PN']
        if pn != 'notfound':
            pn_list.append(pn)  # notfoundだった場合は追加もしない
    if len(pn_list) > 0:  # 「全部notfound」じゃなければ
        pnmean = np.mean(pn_list)
    else:
        pnmean = 0  # 全部notfoundならゼロにする
    return pnmean


def get_pnsum(diclist):
    pn_list = []
    for word in diclist:
        pn = word['PN']
        if pn != 'notfound':
            pn_list.append(pn)  # notfoundだった場合は追加もしない
    if len(pn_list) > 0:  # 「全部notfound」じゃなければ
        pnsum = sum(pn_list)
    else:
        pnsum = 0  # 全部notfoundならゼロにする
    return pnsum


if __name__=="__main__":
    server = '10.2.6.241'
    user = 'read'
    password = 'read'
    database = 'TRIAL'


    top_list = get_top_list(server, user, password, database)
    title = [['ID', 'YEAR', 'WEEK', 'TEXT']]
    # with open(r'D:/20180607toplist.csv', 'w', newline='', encoding='utf-8') as f:
    with open(r'D:/20180629toplist.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(title)#先写标题
        writer.writerows(top_list)

    tw_df = pd.read_csv(r'D:/20180629toplist.csv', encoding='utf-8')
    m = MeCab.Tagger('-Ochasen')  #有词性标注的

    pn_df = pd.read_csv(r'D:/20180605dict.txt', \
                        sep=':',
                        encoding='utf-8',
                        names=('Word', 'Reading', 'POS', 'PN')
                        )
    word_list = list(pn_df['Word'])
    pn_list = list(pn_df['PN'])  # 中身の型はnumpy.float64
    pn_dict = dict(zip(word_list, pn_list))

    pnmeans_list = []
    pnsum_list = []
    id_list = []
    year_list = []
    week_list = []
    for id in tw_df['ID']:
        id_list.append(id)

    for year in tw_df['YEAR']:
        year_list.append(year)

    for week in tw_df['WEEK']:
        week_list.append(week)

    i = 0
    for tw in tw_df['TEXT']:
        dl_old = get_diclist(tw)
        dl_new = add_pnvalue(dl_old)
        for item in dl_new:
            print(id_list[i],year_list[i],week_list[i], item['Surface'],item['BaseForm'], item['PN'], sep='\t')
        pnmean = get_pnmean(dl_new)
        pnmeans_list.append(pnmean)
        pnsum = get_pnsum(dl_new)
        pnsum_list.append(pnsum)
        i += 1

    text_list = list(tw_df['TEXT'])
    for i in range(len(text_list)):
        text_list[i] = text_list[i].replace('\n', ' ')

    aura_df = pd.DataFrame({'ID': tw_df['ID'],
                            'YEAR': tw_df['YEAR'],
                            'WEEK':tw_df['WEEK'],
                            # 'TEXT': text_list,
                            'PN': pnmeans_list,
                            'sumPN':pnsum_list
                            },
                           columns=['ID', 'YEAR', 'WEEK', 'PN','sumPN']
                           )
    aura_df = aura_df.sort_values(by=['ID','YEAR','WEEK'], ascending=True)

    aura_df.to_csv(r'D:/20180629PN现在.csv', \
                   index=None, \
                   encoding='utf-8', \
                   quoting=csv.QUOTE_NONNUMERIC \
                   )
