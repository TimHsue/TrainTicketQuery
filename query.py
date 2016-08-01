
# -*- coding: utf-8 -*-

import json
import urllib2
import re
import time
import threading
import smtplib
import os
from email.mime.text import MIMEText

q_url = 'https://kyfw.12306.cn/otn/lcxxcx/query?'
user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)' \
             'Chrome/49.0.2623.87 Safari/537.36',
adult = 'ADULT'
student = '0X00'
# here is your user name
fr_user = ' '
# here is your password
fr_pwd = ' '
# here is your target
to_e_address = ' '
# here is your target's smtp server ( Tencent: smtp.qq.com )
SMTP_server = 'smtp.qq.com'
# here is your target's smtp server port ( Tencent: 465 )
SMTP_port = 465
code = {}
# init
in_file = open('in')
try:
    global si
    si = in_file.read()
finally:
    in_file.close()
    pattern = re.compile(r'.+?\|.+?\|(.+?)\|.+?\|.+?\|.+?@')
    station_to_code = re.findall(pattern, si)
    pattern = re.compile(r'.+?\|(.+?)\|.+?\|.+?\|.+?\|.+?@')
    station_name = re.findall(pattern, si)
    code = dict(zip(station_name, station_to_code))

ticket_types = ['商务座', '特等座', '一等座', '二等座', '高级软卧', '软卧', '硬卧', '软座',
                '硬座', '无座', '其它']
ticket_codes = ["swz_num", "tz_num", "zy_num", "ze_num", "gr_num", "rw_num", "yw_num", "rz_num",
                "yz_num", "wz_num", "qt_num"]
type_to_code = dict(zip(ticket_types, ticket_codes))
code_to_type = dict(zip(ticket_codes, ticket_types))
# init end


def download_page(date, fr_name, to_name):
    url = q_url + 'purpose_codes=ADULT'
    url += '&queryDate=' + date
    url += '&from_station=' + fr_name
    url += '&to_station=' + to_name
    opener = urllib2.build_opener()
    opener.addheaders = [('User_Agent', user_agent)]
    try:
        response = opener.open(url)
    except urllib2.HTTPError, e:
        print 'url error:'
        print e.code
        print e.reason
        return False
    else:
        res = json.load(response)
        if res == -1:
            return False
    return res


# get left
def find_res(page, train_code, ticket_type):
    if not page:
        print 'url error'
        return False
    for item in page['data']['datas']:
        if item['station_train_code'] == train_code:
            if item[ticket_type] == '0':
                print 'no ticket now'
                return False
            return item[ticket_type]
    print 'unknown error'
    return False


# send message to your target
def send_message(left, train_code, ticket_type):
    message = MIMEText(train_code + '还有' + code_to_type[ticket_type] + '票' + str(left) + '张')
    message['Subject'] = train_code + '有票啦～'
    message['From'] = fr_user
    message['To'] = to_e_address
    try:
        s = smtplib.SMTP_SSL(SMTP_server, SMTP_port)
        s.login(fr_user, fr_pwd)
        s.sendmail(fr_user, to_e_address, message.as_string())
        s.quit()
        print train_code + 'done'
    except smtplib.SMTPException, e:
        print 'fail, %s' % e


class GetStatu(threading.Thread):
    def __init__(self, date, fr_name, to_name, train_code, ticket_type):
        threading.Thread.__init__(self)
        self.date = date
        self.fr_name = fr_name
        self.to_name = to_name
        self.train_code = train_code
        self.ticket_type = ticket_type
        self.stopped = False

    def is_stopped(self):
        return self.stopped

    def stop(self):
        self.stopped = True

    def run(self):
        while True:
            page = download_page(self.date, self.fr_name, self.to_name)
            left = find_res(page, self.train_code, self.ticket_type)
            if left:
                send_message(left, self.train_code, self.ticket_type)
            time.sleep(300)
            if self.stopped:
                break


thread_list = []
del_que = []
be = 0
en = 0
t_cnt = 0
code_to_num = {}
num_to_code = {}


def get_num():
    global be
    global en
    global del_que
    global t_cnt
    if be < en:
        be += 1
        global del_que
        return del_que[be]
    else:
        t_cnt += 1
        global thread_list
        thread_list += [GetStatu('', '', '', '', '')]
        return t_cnt - 1


# recovery pool
def del_num(num):
    global be
    global en
    global del_que
    del_que += [num]
    en += 1


def get_code(st):
    global code
    return code[st]


def get_type_code(st):
    global type_to_code
    return type_to_code[st]


def new_thread():
    data = raw_input('data(xxxx-xx-xx):')
    fr_station = raw_input('from station:')
    to_station = raw_input('to station:')
    fr_station = get_code(fr_station)
    to_station = get_code(to_station)
    ticket_type = raw_input('ticket type(商务座, 特等座, 一等座, 二等座, '
                            '高级软卧, 软卧, 硬卧, 软座, 硬座, 无座, 其它):')
    ticket_type = type_to_code[ticket_type]
    train_code = raw_input('train code:')
    infor = data + fr_station + to_station + train_code + ticket_type
    if infor in code_to_num:
        num = code_to_num[infor]
        if not thread_list[num].is_stopped():
            print 'already existed'
            return
    num = get_num()
    code_to_num[infor] = num
    num_to_code[num] = infor
    thread_list[num] = GetStatu(data, fr_station, to_station, train_code, ticket_type)
    thread_list[num].setDaemon(True)
    thread_list[num].start()


def kill_thread():
    print 'now queried:'
    j = 0
    if code_to_num:
        for i in range(0, t_cnt):
            if not thread_list[i].is_stopped():
                print num_to_code[i]
                j += 1
    if not j:
        print 'none'
    data = raw_input('data(xxxx-xx-xx):')
    fr_station = raw_input('from station:')
    to_station = raw_input('to station:')
    fr_station = get_code(fr_station)
    to_station = get_code(to_station)
    ticket_type = raw_input('ticket type(商务座, 特等座, 一等座, 二等座, '
                            '高级软卧, 软卧, 硬卧, 软座, 硬座, 无座, 其它):')
    ticket_type = type_to_code[ticket_type]
    train_code = raw_input('train code:')
    infor = data + fr_station + to_station + train_code + ticket_type
    if not (infor in code_to_num):
        print 'not existed'
    num = code_to_num[infor]
    thread_list[num].stop()
    del_num(num)


def get_handle():
    while True:
        print 'input \'stop\' to stop, input \'new\' to query a new task, ' \
              'input \'kill\' to kill a task'
        print 'now queried:'
        j = 0
        if code_to_num:
            for i in range(0, t_cnt):
                if not thread_list[i].is_stopped():
                    print num_to_code[i]
                    j += 1
        if not j:
            print 'none'
        tmp = raw_input()
        if tmp == 'stop':
            os.system('clear')
            return 0
        elif tmp == 'new':
            os.system('clear')
            return 1
        elif tmp == 'kill':
            os.system('clear')
            return 2
        else:
            os.system('clear')
            print 'input error, please try again'


class Main(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.stop = False

    def run(self):
        while True:
            han = get_handle()
            if han == 0:
                for item in thread_list:
                    item.stop()
                break
            elif han == 1:
                new_thread()
                os.system('clear')
            else:
                kill_thread()
                os.system('clear')


if __name__ == '__main__':
    main = Main()
    main.start()
