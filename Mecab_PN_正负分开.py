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


def get_top_list(server, user, password, database):
    try:
        conn = pymssql.connect(server, user, password, database)
        cur = conn.cursor()
        sql = " select convert(int,employee_code) as employee_code,report_week,remark from report " \
              " where report_year=2018 and report_week between 1 and 22 and  employee_code in ('10023844','780') " \
              " order by employee_code,report_week "
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
    return (pnmean)

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


def get_pnNegativeMean(diclist):#负数平均
    pn_list = []
    for word in diclist:
        pn = word['PN']
        if pn != 'notfound':
            if pn<0:
                pn_list.append(pn)  # notfoundだった場合は追加もしない
    if len(pn_list) > 0:  # 「全部notfound」じゃなければ
        pnmean = np.mean(pn_list)
    else:
        pnmean = 0  # 全部notfoundならゼロにする
    return (pnmean)

def get_pnNegativeSum(diclist):#负数和
    pn_list = []
    for word in diclist:
        pn = word['PN']
        if pn != 'notfound':
            if pn<0:
                pn_list.append(pn)  # notfoundだった場合は追加もしない
    if len(pn_list) > 0:  # 「全部notfound」じゃなければ
        pnsum = sum(pn_list)
    else:
        pnsum = 0  # 全部notfoundならゼロにする
    return (pnsum)

def get_pnPositiveMean(diclist):#正数平均
    pn_list = []
    for word in diclist:
        pn = word['PN']
        if pn != 'notfound':
            if pn>=0:
                pn_list.append(pn)  # notfoundだった場合は追加もしない
    if len(pn_list) > 0:  # 「全部notfound」じゃなければ
        pnmean = np.mean(pn_list)
    else:
        pnmean = 0  # 全部notfoundならゼロにする
    return (pnmean)

def get_pnPositiveSum(diclist):#正数和
    pn_list = []
    for word in diclist:
        pn = word['PN']
        if pn != 'notfound':
            if pn>=0:
                pn_list.append(pn)  # notfoundだった場合は追加もしない
    if len(pn_list) > 0:  # 「全部notfound」じゃなければ
        pnsum = sum(pn_list)
    else:
        pnsum = 0  # 全部notfoundならゼロにする
    return (pnsum)

if __name__=="__main__":
    server = 'x.x.x.x'
    user = 'x'
    password = 'x'
    database = 'x'

    top_list = get_top_list(server, user, password, database)
    title = [['ID', 'WEEK', 'TEXT']]
    with open(r'D:/20180607toplist.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(title)#先写标题
        writer.writerows(top_list)

    # tw_df = pd.read_csv(r'D:/01.csv', encoding='utf-8')
    tw_df = pd.read_csv(r'D:/20180607toplist.csv', encoding='utf-8')
    m = MeCab.Tagger('')  # 指定しなければIPA辞書

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
    pnNegativeMean_list = []
    pnNegativeSum_list = []
    pnPositiveMean_list = []
    pnPositiveSum_list = []
    id_list = []
    for id in tw_df['ID']:
        id_list.append(id)

    i = 0
    for tw in tw_df['TEXT']:
        dl_old = get_diclist(tw)
        dl_new = add_pnvalue(dl_old)
        # for item in dl_new:
        #     print(id_list[i], item['Surface'], item['POS1'], item['PN'], sep='\t')
        pnmean = get_pnmean(dl_new)#平均
        pnmeans_list.append(pnmean)
        pnsum = get_pnsum(dl_new)#和
        pnsum_list.append(pnsum)
        pnNegativeMean = get_pnNegativeMean(dl_new) #负数平均
        pnNegativeMean_list.append(pnNegativeMean)
        pnNegativeSum = get_pnNegativeSum(dl_new) # 负数和
        pnNegativeSum_list.append(pnNegativeSum)
        pnPositiveMean = get_pnPositiveMean(dl_new) # 正数平均
        pnPositiveMean_list.append(pnPositiveMean)
        pnPositiveSum = get_pnPositiveSum(dl_new) # 正数和
        pnPositiveSum_list.append(pnPositiveSum)
        i += 1

    text_list = list(tw_df['TEXT'])
    for i in range(len(text_list)):
        text_list[i] = text_list[i].replace('\n', ' ')

    aura_df = pd.DataFrame({'ID': tw_df['ID'],
                            'WEEK':tw_df['WEEK'],
                            # 'TEXT': text_list,
                            'pnNegativeMean': pnNegativeMean_list,
                            'pnNegativeSum':pnNegativeSum_list,
                            'pnPositiveMean': pnPositiveMean_list,
                            'pnPositiveSum': pnPositiveSum_list
                            },
                           # columns=['ID','WEEK', 'TEXT', 'PN','sumPN']
                           columns=['ID','WEEK', 'pnNegativeMean','pnNegativeSum','pnPositiveMean','pnPositiveSum']
                           )
    aura_df = aura_df.sort_values(by=['ID','WEEK'], ascending=True)

    aura_df.to_csv(r'D:/aura.csv', \
                   index=None, \
                   encoding='utf-8', \
                   quoting=csv.QUOTE_NONNUMERIC \
                   )
