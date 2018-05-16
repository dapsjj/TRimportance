import collections
import termextract.japanese_plaintext
import termextract.core
import re
import MeCab

# ファイルを読み込む
text = open(r"../testMecab/会長.txt", "r", encoding="utf-8").read()
TOTAL_MARK = "."  # トータル文書数を示す"."をセット
OTAL_MARK = "."  # トータル文書数を示す"."をセット
IGNORE_WORDS = set([])  # 重要度計算外とする語

# ひらがな
JP_HIRA = set([chr(i) for i in range(12353, 12436)])
# カタカナ
JP_KATA = set([chr(i) for i in range(12449, 12532+1)])
JP_KATA.add('ー')
#要忽略的字符
# "ー"特殊
MULTIBYTE_MARK = set([
     "、", "。", "”", "“", "，", "《", "》", "：", "（", "）", "；",".","/","・","～"
    "〈", "〉", "「", "」", "『", "』", "【", "】", "〔", "〕", "？", "！",
    "ー", "-", "ー", "…", "‘", "’", "／","/"
    "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "０", "１", "２", "３",
    "４", "５", "６", "７", "８", "９",
    "①","②","③","④","⑤","⑥","⑦","⑧","⑨","⑩","⑪","⑫",
    "\r\n","\t","\n",
    "a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z",
    "A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"
    ])


def cmp_noun_list(data):
    """
    和文テキストを受け取り、複合語（空白区切りの単名詞）のリストを返す
    """
    savetxt_list=[]
    deltxt_list = []
    # mecab = MeCab.Tagger("-Ochasen") #有词性标注的
    mecab = MeCab.Tagger("-Owakati")  # 没有词性标注的
    cmp_nouns = mecab.parse(data)
    cmp_nouns = cmp_nouns.split(" ")
    for every_keyword in cmp_nouns:
        if (every_keyword is not None and len(every_keyword.strip())==1 and (every_keyword in MULTIBYTE_MARK or every_keyword in JP_HIRA or every_keyword in JP_KATA)):
            deltxt_list.append(every_keyword)
        else:
            savetxt_list.append(every_keyword)
    cmp_nouns = savetxt_list
    terms = []
    _increase(cmp_nouns, terms)
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
