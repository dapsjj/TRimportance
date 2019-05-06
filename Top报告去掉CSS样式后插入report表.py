#!/usr/bin/env python
# coding: utf-8

import paramiko
import pymssql
import datetime
import time
import logging
import os
import configparser
import re
import decimal #不加打包成exe会出错


conn = None  # 连接
cur = None  # 游标


def write_log():
    '''
    写log
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


def read_dateConfig_file_set_database():
    '''
    读dateConfig.ini,设置数据库信息
    '''
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
    else:
        logger.error("DateConfig.ini doesn't exist!")


def getConn():
    '''
    声明数据库连接对象
    '''
    global conn
    global cur
    try:
        conn = pymssql.connect(server, user, password, database)
        cur = conn.cursor()
    except pymssql.Error as ex:
        logger.error("dbException:" + str(ex))
        raise ex
    except Exception as ex:
        logger.error("Call method getConn() error!")
        raise ex


def closeConn():
    '''
    关闭数据库连接对象
    '''
    global conn
    global cur
    try:
        cur.close()
        conn.close()
    except pymssql.Error as ex:
        logger.error("dbException:" + str(ex))
        raise ex
    except Exception as ex:
        logger.error("Call method closeConn() error!")
        raise ex
    finally:
        cur.close()
        conn.close()


def read_dateConfig_file_set_linux_info():
    '''
    读dateConfig.ini,获取linux文件名、服务器地址、端口、用户名、密码
    '''
    if os.path.exists(os.path.join(os.path.dirname(__file__), "dateConfig.ini")):
        try:
            conf = configparser.ConfigParser()
            conf.read(os.path.join(os.path.dirname(__file__), "dateConfig.ini"), encoding="utf-8-sig")
            execute_year = conf.get("execute_year", "year")
            execute_week = conf.get("execute_week", "week")
            linux_file_path = conf.get("linux_file_path", "linux_file_path")
            linux_hostname = conf.get("linux_hostname", "linux_hostname")
            linux_port = conf.get("linux_port", "linux_port")
            linux_username = conf.get("linux_username", "linux_username")
            linux_password = conf.get("linux_password", "linux_password")

            return execute_year,execute_week,linux_file_path,linux_hostname,linux_port,linux_username,linux_password
        except Exception as ex:
            logger.error("Content in dateConfig.ini has error.")
            logger.error("Exception:" + str(ex))
            raise ex
    else:
        logger.error("DateConfig.ini doesn't exist!")


def get_data_from_smart():
    '''
    从linux服务器获取top报告的数据
    :return: top报告的list
    '''
    # 创建SSH对象
    try:
        ssh = paramiko.SSHClient()
        # 允许连接不在know_hosts文件中的主机
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # 连接服务器
        ssh.connect(hostname=linux_hostname, port=int(linux_port), username=linux_username, password=linux_password)
        my_linux_top_list = []
        # 执行命令
        # cmd = " zcat /TORASINNYOU/LV3/TOP/REPORT/2019.gz |awk '$1==2019&&$2==17' "
        cmd = " zcat "+linux_file_path  + " |awk "+" '$1=="+str(int(execute_year))+"&&$2=="+str(int(execute_week))+"' "
        stdin, stdout, stderr = ssh.exec_command(cmd)
        result = stdout.read()
        result = str(result, encoding="utf-8")
        linux_str_list = result.split('\n')
        for row in linux_str_list:
            if row:
                myList = row.split(" ")
                my_linux_top_list.append(myList)
        return my_linux_top_list
    except Exception as ex:
        logger.error("Call method get_data_from_smart() error!")
        logger.error("Exception:" + str(ex))
        raise ex


def delete_data_from_report():
    '''
    从"report"表，删除生成年、生成周对应的数据
    '''
    try:
        sql = ' delete from report where report_year = %s and report_week = %s' \
              % (execute_year, execute_week)
        cur.execute(sql)
        conn.commit()
    except pymssql.Error as ex:
        logger.error("dbException:" + str(ex))
        raise ex
    except Exception as ex:
        logger.error("Call method delete_data_from_report() error!")
        logger.error("Exception:" + str(ex))
        conn.rollback()
        raise ex


def remove_css_for_column(para_str):
    '''
    删除字符串中的css样式,但保留<br>,<br/>,<BR>,<BR/>
    :param para_str: 需要去掉css的字符串
    :return: 去掉了css但是保留了<br>,<br/>,<BR>,<BR/>的字符串
    '''
    try:
        if para_str:
            para_str = para_str.replace("&nbsp;"," ") #替换html中的空格
            para_str = para_str.replace("_"," ") #替换下划线为空格
            para_str = re.sub('(?i)(<br/?>)|<[^>]*>', r'\1', para_str)#去掉尖括号开始尖括号结束的内容,不包括<br>,<br/>,<BR>,<BR/>
            return para_str
    except Exception as ex:
        logger.error("Call method remove_css_for_column() error!")
        logger.error("Exception:" + str(ex))
        raise ex


def remove_css_in_top(para_list):
    '''
    删除para_list中的css样式,但保留<br>,<br/>,<BR>,<BR/>
    :param para_list: 要处理的含有css的Top的list
    :return: 去掉了css但是保留了<br>,<br/>,<BR>,<BR/>的list
    '''
    try:
        linux_top_list_for_report = []

        if para_list:
            new_linux_top_list_1 = []
            for row in para_list:
                remark = ""
                for i, element in enumerate(row):
                    if i==3:#是remark那一列
                        remark = remove_css_for_column(row[i])
                new_linux_top_list_1.append(row[0:3]+[remark]+row[4:])

        if new_linux_top_list_1:
            for row in new_linux_top_list_1:
                new_linux_top_list_2 = []
                for i, element in enumerate(row):
                    if i != 4 and i != 5:
                        new_linux_top_list_2.append(row[i])
                    else:
                        new_linux_top_list_2.append(
                            row[i][0:4] + '-' + row[i][4:6] + '-' + row[i][6:8] + ' ' +
                            row[i][8:10] + ':' + row[i][10:12] + ':' + row[i][12:14] + '.000')
                linux_top_list_for_report.append(new_linux_top_list_2)

        return linux_top_list_for_report
    except Exception as ex:
        logger.error("Call method remove_css_in_top() error!")
        logger.error("Exception:" + str(ex))
        raise ex


def insert_into_report(para_list):
    if para_list:
        try:
            list_to = [tuple(item) for item in para_list]
            sql = ' insert into report (report_year,report_week,employee_code,remark,reg_date,upt_date) ' \
                  ' values(%s,%s,%s,%s,%s,%s) '
            cur.executemany(sql, list_to)
            conn.commit()
        except pymssql.Error as ex:
            logger.error("dbException:" + str(ex))
            raise ex
        except Exception as ex:
            logger.error("Call method insert_into_report() error!")
            logger.error("Exception:" + str(ex))
            conn.rollback()
            raise ex


if __name__=="__main__":
    logger = write_log()  # 获取日志对象
    time_start = datetime.datetime.now()
    start = time.time()
    logger.info("Program start,now time is:"+str(time_start))
    server,user,password,database = read_dateConfig_file_set_database()#读取配置文件中的数据库信息
    execute_year,execute_week,linux_file_path,linux_hostname,linux_port,linux_username,linux_password = read_dateConfig_file_set_linux_info()#读取配置文件中的linux信息
    getConn()  #打开数据库连接对象
    linux_top_list = get_data_from_smart()
    removed_css_in_top_list = remove_css_in_top(linux_top_list)
    delete_data_from_report()#删除配置文件指定的execute_year，execute_week数据
    insert_into_report(removed_css_in_top_list)#插入到report表去掉css样式后的数据(保留<br>,<br/>,<BR>,<BR/>)
    closeConn() #关闭数据库
    time_end = datetime.datetime.now()
    end = time.time()
    logger.info("Program end,now time is:" + str(time_end))
    logger.info("Program run : %f seconds" % (end - start))
