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

def Beijing_time():
    r=requests.get('https://www.baidu.com')
    t=time.strptime(r.headers['date'],'%a, %d %b %Y %H:%M:%S GMT')
    return time.mktime(t)+28800

if( Beijing_time()-1569830263 >=86400*2):
    input('测试期已过，请联系作者。')
    sys.exit()

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
    for i in d['data']:
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

def worker1(cookies,lotteryid,model,stop_to_bet,set_moneys,chedao,treeview1,treeview2):
    '''
    方案一主函数
    '''
    bet_list_flag = ''
    chedao=chedao.split(' ')
    money_dict = dict()
    for i in range(10):
        money_dict[str(i)] = set_moneys[::-1]

    while(1):
        next_issue = getCurInfoAndModel(lotteryid, cookies)[0]
        numbs_dict = Get_last30_number(lotteryid, cookies)
        now_issue = '%0*d' % (4, int(next_issue.split('-')[1])-1)
        treeview_del(treeview)
        treeview_insert(treeview,numbs_dict)
        try:
            now_numbs = numbs_dict[now_issue].split(',')
        except KeyError:
            print('彩种：%s' % lotteryid,'开奖结果尚未更新，正在重试……')
            time.sleep(60)
            continue

        if(now_numbs == bet_list_flag):
            print(time.asctime(time.localtime(time.time())),lotteryid,
                '当前期号：', next_issue, '等待开奖中……')
            time.sleep(60)
            continue
        else:
            for n, i in enumerate(bet_list_flag):
                if i == now_numbs[n]:
                    money_dict[str(n)] = set_moneys[::-1]

        bet_list = list() #位置 投注内容 金额
        for n, i in enumerate(now_numbs):
            if(len(money_dict[str(n)]) == 0):
                money_dict[str(n)] = set_moneys[::-1]
            if(str(n) in chedao):
                bet_list.append([str(n), i, str(money_dict[str(n)].pop())])
        if(model=='1'):
            if(str(lotteryid)=='3'):
                d = Bet(lotteryid, ''.join(next_issue.split('-')), bet_list, cookies)
            else:
                d = Bet(lotteryid, next_issue, bet_list, cookies)
        else:
            d='200'
            print(
    ''' 
    模拟投注成功
    彩种：%s
    期号：%s
    投注内容：'''
                % (lotteryid,next_issue)
            )
            for i in bet_list:
                print('位置:'+str(i[0]),'内容:'+str(i[1]), str(i[2])+'元')
        bet_list_flag = now_numbs[:]
        if(d != '200'):
            time.sleep(10)
            continue

def treeview_insert(treeview,d):
        for i in range(len(d)): # 写入数据
            treeview.insert('', i, values=(i, d[i]))

def treeview_del(treeview):
    x=treeview.get_children()
    for item in x:
        treeview.delete(item)

def fangan1(cookies):
    #方案一 主线程
    base=tk.Tk()
    base.title('方案一：开什么投什么 qq792301982')
    base.geometry('760x800')

    notebook=ttk.Notebook(base)
    #22极速赛车
    frame1=Frame(notebook)
    col=1
    Label(frame1, text="22极速赛车开奖信息：").grid(row=1,column=col)
    columns=['期号','开奖号']
    treeview_jisu1 =ttk.Treeview(frame1, height=10, show="headings", columns=columns)  # 表格
    treeview_jisu1.column("期号", width=50, anchor='center') # 表示列,不显示
    treeview_jisu1.column("开奖号", width=200, anchor='center')
    treeview_jisu1.heading("期号", text="期号") # 显示表头
    treeview_jisu1.heading("开奖号", text="开奖号")
    treeview_jisu1.grid(row=2,column=col)

    columns=['期号','赛道','投注内容','是否中奖','余额']
    treeview_jisu2 =ttk.Treeview(frame1, height=10, show="headings", columns=columns)  # 表格
    treeview_jisu2.column("期号", width=50, anchor='center') # 表示列,不显示
    treeview_jisu2.column("赛道", width=30, anchor='center')
    treeview_jisu2.column("投注内容", width=100, anchor='center')
    treeview_jisu2.column("是否中奖", width=50, anchor='center')
    treeview_jisu2.column("余额", width=50, anchor='center')
    treeview_jisu2.heading("期号", text="期号") # 显示表头
    treeview_jisu2.heading("赛道", text="赛道")
    treeview_jisu2.heading("投注内容", text="投注内容")
    treeview_jisu2.heading("是否中奖", text="是否中奖")
    treeview_jisu2.heading("余额", text="余额")
    treeview_jisu2.grid(row=3,column=col)

    Label(frame1, text="极速赛车止赢止损（空格分隔）：").grid(row=4,column=col)
    text_jisu_stop2bet=Text(frame1,width=10,height=2)
    text_jisu_stop2bet.grid(row=5,column=col)

    Label(frame1, text="极速赛车模式（1真实 2模拟）：").grid(row=6,column=col)
    text_jisu_model=Text(frame1,width=10,height=2)
    text_jisu_model.grid(row=7,column=col)

    Label(frame1, text="极速赛车金额（空格分隔）：").grid(row=8,column=col)
    text_jisu_moneys=Text(frame1,width=10,height=2)
    text_jisu_moneys.grid(row=9,column=col)

    Label(frame1, text="极速赛车车道（空格分隔）：").grid(row=10,column=col)
    text_jisu_chedao=Text(frame1,width=10,height=2)
    text_jisu_chedao.grid(row=11,column=col)

    def start_data(cookies,lotteryid,model,stop_to_bet,set_moneys,chedao,treeview_jisu1,treeview_jisu2):
        t1=threading.Thread(target=worker1,args=(cookies,str(lotteryid),model,stop_to_bet,set_moneys,chedao,treeview_jisu1,treeview_jisu2,))
        t1.start()

    Button(frame1,text="开始").grid(row=12,column=col)
    Button(frame1,text="暂停").grid(row=13,column=col)

    #3幸运飞艇
    frame2=Frame(notebook)
    col=2
    Label(frame2, text="3幸运飞艇开奖信息：").grid(row=1,column=col)
    columns=['期号','开奖号']
    treeview_xingyun1 =ttk.Treeview(frame2, height=10, show="headings", columns=columns)  # 表格
    treeview_xingyun1.column("期号", width=50, anchor='center') # 表示列,不显示
    treeview_xingyun1.column("开奖号", width=200, anchor='center')
    treeview_xingyun1.heading("期号", text="期号") # 显示表头
    treeview_xingyun1.heading("开奖号", text="开奖号")
    treeview_xingyun1.grid(row=2,column=col)

    columns=['期号','赛道','投注内容','是否中奖']
    treeview_xingyun2 =ttk.Treeview(frame2, height=10, show="headings", columns=columns)  # 表格
    treeview_xingyun2.column("期号", width=50, anchor='center') # 表示列,不显示
    treeview_xingyun2.column("赛道", width=30, anchor='center')
    treeview_xingyun2.column("投注内容", width=100, anchor='center')
    treeview_xingyun2.column("是否中奖", width=50, anchor='center')
    treeview_xingyun2.heading("期号", text="期号") # 显示表头
    treeview_xingyun2.heading("赛道", text="赛道")
    treeview_xingyun2.heading("投注内容", text="投注内容")
    treeview_xingyun2.heading("是否中奖", text="是否中奖")
    treeview_xingyun2.grid(row=3,column=col)

    Label(frame2, text="3幸运飞艇止赢止损（空格分隔）：").grid(row=4,column=col)
    Text(frame2,width=10,height=2).grid(row=5,column=col)

    Label(frame2, text="3幸运飞艇模式（1真实 2模拟）：").grid(row=6,column=col)
    Text(frame2,width=10,height=2).grid(row=7,column=col)

    Label(frame2, text="3幸运飞艇金额（空格分隔）：").grid(row=8,column=col)
    Text(frame2,width=10,height=2).grid(row=9,column=col)

    Label(frame2, text="3幸运飞艇车道（空格分隔）：").grid(row=10,column=col)
    Text(frame2,width=10,height=2).grid(row=11,column=col)
    Button(frame2,text="开始").grid(row=12,column=col)
    Button(frame2,text="暂停").grid(row=13,column=col)

    #31欢乐赛车
    col=3
    frame3=Frame(notebook)
    Label(frame3, text="31欢乐赛车开奖信息：").grid(row=1,column=col)
    columns=['期号','开奖号']
    treeview_huanle1 =ttk.Treeview(frame3, height=10, show="headings", columns=columns)  # 表格
    treeview_huanle1.column("期号", width=50, anchor='center') # 表示列,不显示
    treeview_huanle1.column("开奖号", width=200, anchor='center')
    treeview_huanle1.heading("期号", text="期号") # 显示表头
    treeview_huanle1.heading("开奖号", text="开奖号")
    treeview_huanle1.grid(row=2,column=col)

    columns=['期号','赛道','投注内容','是否中奖']
    treeview_huanle2 =ttk.Treeview(frame3, height=10, show="headings", columns=columns)  # 表格
    treeview_huanle2.column("期号", width=50, anchor='center') # 表示列,不显示
    treeview_huanle2.column("赛道", width=30, anchor='center')
    treeview_huanle2.column("投注内容", width=100, anchor='center')
    treeview_huanle2.column("是否中奖", width=50, anchor='center')
    treeview_huanle2.heading("期号", text="期号") # 显示表头
    treeview_huanle2.heading("赛道", text="赛道")
    treeview_huanle2.heading("投注内容", text="投注内容")
    treeview_huanle2.heading("是否中奖", text="是否中奖")
    treeview_huanle2.grid(row=3,column=col)

    Label(frame3, text="31欢乐赛车止赢止损（空格分隔）：").grid(row=4,column=col)
    Text(frame3,width=10,height=2).grid(row=5,column=col)

    Label(frame3, text="31欢乐赛车模式（1真实 2模拟）：").grid(row=6,column=col)
    Text(frame3,width=10,height=2).grid(row=7,column=col)

    Label(frame3, text="31欢乐赛车金额（空格分隔）：").grid(row=8,column=col)
    Text(frame3,width=10,height=2).grid(row=9,column=col)

    Label(frame3, text="31欢乐赛车车道（空格分隔）：").grid(row=10,column=col)
    Text(frame3,width=10,height=2).grid(row=11,column=col)
    Button(frame3,text="开始").grid(row=12,column=col)
    Button(frame3,text="暂停").grid(row=13,column=col)

    # t1=threading.Thread(target=worker1,args=(cookies,'22',model,stop_to_bet,set_moneys,chedao))
    # t2=threading.Thread(target=worker1,args=(cookies,'3',model,stop_to_bet,set_moneys,chedao))
    # t3=threading.Thread(target=worker1,args=(cookies,'31',model,stop_to_bet,set_moneys,chedao))
    # t1.start()
    # t2.start()
    # t3.start()

    notebook.add(frame1, text="22极速赛车")
    notebook.add(frame2, text="3幸运飞艇")
    notebook.add(frame3, text="31欢乐赛车")
    notebook.pack()
    base.mainloop()

if __name__ == "__main__":
    #一个方案一个进程
    multiprocessing.freeze_support()
    '''
        方案一：开什么投什么 
    '''
    print('钻石国际自动投注')
    print('方案一：开什么投什么')
    print('22极速赛车        3幸运飞艇        31欢乐赛车')
    # model=input('选择模式前的序号 1真实 2模拟：')
    # jisusaiche_chedao=input('选择极速赛车车道（空格分隔）：')
    # xingyun_chedao=input('选择幸运飞艇车道（空格分隔）：')
    # huanle_chedao=input('选择欢乐赛车车道（空格分隔）：')
    # set_moneys = input("输入投注金额（用空格分隔开）：").split(' ')
    #cookies=login()
    cookies=''
    fangan1(cookies)
    # p1=Process(target=worker1,args=(cookies,'22',model,set_moneys,jisusaiche_chedao,))
    # p2=Process(target=worker1,args=(cookies,'31',model,set_moneys,huanle_chedao,))
    # p1.start()
    # p2.start()