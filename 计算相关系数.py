import pandas as pd
import csv
#计算相关系数
# rs = pd.DataFrame.from_csv(r'D:/ttt.csv',encoding='utf-8')
rs = pd.read_csv(r'D:/Clustering_TOP.csv',encoding='utf-8')

with open('D:/Clustering_TOP.csv','r') as csvfile:
    reader = csv.reader(csvfile)
    rows = [row for row in reader]
csv_title = rows[0]
csv_title = csv_title[1:]
len_csv_title = len(csv_title)
for i in range(len_csv_title):
    for j in range(i+1):
        print(str(csv_title[j])+'_'+str(csv_title[i]) + " = " + str(rs[csv_title[i]].corr(rs[csv_title[j]])), end='\t')
    print()
