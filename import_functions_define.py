import requests
import json
import time,sys
from multiprocessing import Process
import multiprocessing
import mul_process_package
import tkinter as tk
from tkinter import *
from tkinter import ttk
import threading
import signal
import ctypes,inspect
import traceback


def Beijing_time():
    r=requests.get('https://www.baidu.com')
    t=time.strptime(r.headers['date'],'%a, %d %b %Y %H:%M:%S GMT')
    return time.mktime(t)+28800

if( Beijing_time()-1570120297 >=86400*2):
    input('测试期已过，请联系作者。')
    sys.exit()

def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")
 
def stop_thread(thread):
    _async_raise(thread.ident, SystemExit)

url = 'https://www.zs6606.com/index.html'
login_test_url = 'https://www.zs6606.com/login/testPlay.do'
login_url = 'https://www.zs6606.com/login/login.do'
bet_url = 'https://www.zs6606.com/lottery/bet.do'
curInfo_url = 'https://www.zs6606.com/lottery/getCurInfoAndModel.do'
get_numb_url = 'https://www.zs6606.com/mobileLottery/historyLast12OpenSearch.do'
balance_url='https://www.zs6606.com/user/getUserBalance.do'
zong_winsearch_url='https://www.zs6606.com/user/getUserTodayWinSearch.do'
winsearch_url='https://www.zs6606.com/user/getUserWinSearchByLotId.do'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
}

'''
                    极速赛车        幸运飞艇        欢乐赛车
lotteryid           22               3             31

1~10名methodid      1142             103           4642
                    |                |             |
                    1242             202           4742       冠军『01』

冠亚组合methodid     1243             204           4743
                    |                |             |
                    1259             224           4759       冠、亚军和『3』


'''

def GetUserBalance(cookies):
    r=requests.post(balance_url,headers=headers,cookies=cookies)
    d=json.loads(r.text)
    return d['data']

def ZongWinSearch(cookies):
    r=requests.post(zong_winsearch_url,headers=headers,cookies=cookies)
    d=json.loads(r.text)
    return d['data']

def WinSearch(cookies,lotteryid):
    r=requests.post(winsearch_url,headers=headers,cookies=cookies,data={'lotteryid': '22'})
    d=json.loads(r.text)
    return d['data']
    
def login():
    username=input("账号：")
    passward=input("密码：")
    if(username==''):
        r = requests.post(login_test_url, headers=headers)
        cookies = r.cookies
        print('试玩模式')
    else:
        r=requests.post(login_url,headers=headers,data={'loginname':username,'pwd':passward})
        cookies=r.cookies
        d=json.loads(r.text)
        print(d['msg'])

    return cookies

def GetLatestOpenCode(lotteryid, cookies):
    pass

def getCurInfoAndModel(lotteryid, cookies):
    #下注期号 and 只能获取冠亚军的赔率
    r = requests.post(curInfo_url, cookies=cookies, headers=headers, data={
                      'lotteryid': str(lotteryid), 'pageflag': 'gyjzh'})
    d = json.loads(r.text)
    curIssue = d['data']['curIssue']
    if(str(lotteryid)=='3'):
        curIssue=curIssue[:8]+'-'+curIssue[8:]
    # modelItemList:[{methodid: 1243, model: 42.3}]
    return [curIssue, d['data']['modelItemList']]


def Get_last30_number(lotteryid, cookies):
    # 近30期开奖号码
    r = requests.post(get_numb_url, headers=headers, cookies=cookies, data={
                      'lotteryid': lotteryid, 'nums': 30})
    d = json.loads(r.text)
    t = dict()
    for i in d['data'][::-1]:
        issue = i['issue']
        numbs = i['winnumber']
        t['%0*d' % (4, int(issue))] = numbs
    return t


def Bet(lotteryid, issue, method_list, cookies):
    '''
          彩种 期号 下注内容列表 cookies

          method_list[
              ['1','01',1],['冠亚军和','3',1]        #第一位，服务器无验证，但需要填入
          ]

    '''
    str_l = list()
    if str(lotteryid) == '22':
        methodid_start = [1142, 1243]  # [ 1~10 , 冠亚组合]
    elif str(lotteryid) == '31':
        methodid_start = [4642, 4743]
    elif str(lotteryid) == '3':
        methodid_start = [103, 204]

    total = 0
    for i in method_list:
        if(i[0] == '冠亚军和'):
            str_l.append(
                {
                    'methodid': str(int(methodid_start[1])+int(i[1])-3),
                    # 'betcontent':'冠、亚军和『%s』' % i[1],
                    'amount': str(i[2])
                }
            )

        else:
            str_l.append(
                {
                    'methodid': str(int(methodid_start[0])+int(i[0])*10+int(i[1])-1),
                    # 'betcontent':'%s『%s』' % (i[0],i[1]),
                    'amount': str(i[2])
                }
            )
        total += int(i[2])

    data = {
        'lotteryid': str(lotteryid),  # "22"
        'issue': str(issue),  # '20190930-0127'
        'total': str(total),   # 总金额
        'list': str(str_l)                     # '''[{"methodid":"1142","betcontent":"冠军『01』","amount":"1"},{"methodid":"1233","betcontent":"第十名『01』","amount":"1"}]''',
    }
    r = requests.post(bet_url, headers=headers, data=data, cookies=cookies)
    d = json.loads(r.text)
    if(d['code'] == "200"):
        print(
            ''' 
!!!!!!!!!!!!!!投注成功!!!!!!!!!!!!!!
彩种：%s
总金额：%s
总数：%s
期号：%s
投注内容：'''
            % (lotteryid,d['data']['totalBetMoney'], d['data']['num'], d['data']['issue'])
        )
        for i in d['data']['gameRecords']:
            print(i['betcontent'], str(i['amount'])+'元')
        print("余额：%s 彩种%s今日输赢：%s 今日总输赢：%s" % (GetUserBalance(cookies),lotteryid,WinSearch(cookies,lotteryid),ZongWinSearch(cookies)) )
    else:
        print(d['msg'])
    return d['code']

def treeview_insert(treeview,d):
        for n,i in enumerate(d): # 写入数据
            treeview.insert('', 0, values=(i, d[i]))

def treeview2_insert(treeview,d):
    for n,i in enumerate(d): # 写入数据
        for u in d[i]:
            treeview.insert('', 0, values=(i, u[0], u[1], u[2]))

def treeview_del(treeview):
    x=treeview.get_children()
    for item in x:
        treeview.delete(item)