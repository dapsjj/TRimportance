import re
import csv
import time
import pandas as pd
import matplotlib.pyplot as plt
import MeCab
import random
import numpy as np

'''
http://www.statsbeginner.net/entry/2017/05/07/091435
#这个网页的代码坑很多
'''

tw_df = pd.read_csv(r'D:/01.csv', encoding='ANSI')
# MeCabインスタンス作成
m = MeCab.Tagger('')  # 指定しなければIPA辞書
# -----テキストを形態素解析して辞書のリストを返す関数----- #
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

pn_df = pd.read_csv(r'D:/20180605dict.txt',\
                    sep=':',
                    encoding='utf-8',
                    names=('Word','Reading','POS', 'PN')
                   )
# pn_df.loc[pn_df.Word == '細胞', 'PN']
word_list = list(pn_df['Word'])
pn_list = list(pn_df['PN'])  # 中身の型はnumpy.float64
pn_dict = dict(zip(word_list, pn_list))
# print(pn_dict)

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
    return(diclist_new)

# test_text = '今あります。'
# dl_test = get_diclist(test_text)
# dl_test = add_pnvalue(dl_test)

def get_pnmean(diclist):
    pn_list = []
    for word in diclist:
        pn = word['PN']
        if pn != 'notfound':
            pn_list.append(pn)  # notfoundだった場合は追加もしない
    if len(pn_list) > 0:        # 「全部notfound」じゃなければ
        pnmean = np.mean(pn_list)
    else:
        pnmean = 0              # 全部notfoundならゼロにする
    return(pnmean)

pnmeans_list = []
id_list = []
for id in tw_df['ID']:
    id_list.append(id)

i = 0
for tw in tw_df['TEXT']:
    dl_old = get_diclist(tw)
    dl_new = add_pnvalue(dl_old)
    for item in dl_new:
        print(id_list[i],item['Surface'],item['POS1'],item['PN'],sep='\t')
    pnmean = get_pnmean(dl_new)
    pnmeans_list.append(pnmean)
    i += 1

text_list = list(tw_df['TEXT'])
for i in range(len(text_list)):
    text_list[i] = text_list[i].replace('\n', ' ')


# ツイートID、本文、PN値を格納したデータフレームを作成
aura_df = pd.DataFrame({'ID':tw_df['ID'],
                        'TEXT':text_list,
                        'PN':pnmeans_list,
                       },
                       columns=['ID', 'TEXT', 'PN']
                      )
# PN値の昇順でソート
aura_df = aura_df.sort_values(by='PN', ascending=True)


# CSVを出力（ExcelでみたいならUTF8ではなくShift-JISを指定すべき）
aura_df.to_csv(r'D:/aura.csv',\
                index=None,\
                encoding='utf-8',\
                quoting=csv.QUOTE_NONNUMERIC\
               )
