# -*- coding: UTF-8 -*-
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
import os
import csv
import pymssql
import pandas as pd



def get_top_list(server, user, password, database):
    try:
        conn = pymssql.connect(server, user, password, database)
        cur = conn.cursor()
        sql = " select convert(int,employee_code) as employee_code,report_year,report_week,remark from report " \
              " where (report_year=2018 and report_week between 1 and 20 and  employee_code in ('10023844')) " \
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


def output_score_magnitude(tableView,csv_name):
    client = language.LanguageServiceClient()
    employee_list = []
    year_list = []
    week_list = []
    text_list = []
    score_list  = []
    magnitude_list = []
    i = 0
    for t_text in tableView['TEXT']:
        t_text = t_text.replace("<br/>", "")
        t_text = t_text.replace("<br>", "")
        document = types.Document(content=t_text,type=enums.Document.Type.PLAIN_TEXT)
        sentiment = client.analyze_sentiment(document=document)
        for index, sentence in enumerate(sentiment.sentences):
            every_score = sentence.sentiment.score
            every_magnitude = sentence.sentiment.magnitude
            # print(index, sentence.text.content, every_score, every_magnitude)
            employee_list.append(tableView['ID'][i])
            year_list.append(tableView['YEAR'][i])
            week_list.append(tableView['WEEK'][i])
            text_list.append(sentence.text.content)
            score_list.append(every_score)
            magnitude_list.append(every_magnitude)
        i += 1

    aura_df = pd.DataFrame({'ID': employee_list,
                            'YEAR': year_list,
                            'WEEK': week_list,
                            'TEXT': text_list,
                            'SCORE': score_list,
                            'MAGNITUDE': magnitude_list
                            },
                           columns=['ID', 'YEAR', 'WEEK', 'TEXT', 'SCORE', 'MAGNITUDE']
                           )
    aura_df = aura_df.sort_values(by=['ID', 'YEAR', 'WEEK'], ascending=True)

    aura_df.to_csv(csv_name, index=None, encoding='utf-8', quoting=csv.QUOTE_NONNUMERIC)




if __name__=="__main__":
    server = 'x.x.x.x'
    user = 'x'
    password = 'x'
    database = 'x'

    top_list = get_top_list(server, user, password, database)
    title = [['ID', 'YEAR', 'WEEK', 'TEXT']]
    with open(r'D:/20180611toplist.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(title)  # 先写标题
        writer.writerows(top_list)

    tw_df = pd.read_csv(r'D:/20180611toplist.csv', encoding='utf-8')
    csv_name = r'D:/20180613Score.csv'
    output_score_magnitude(tw_df,csv_name)
