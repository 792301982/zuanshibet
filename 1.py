import requests
import json
import time,sys
from multiprocessing import Process

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
    else:
        print(d['msg'])
    return d['code']

def worker1(cookies,lotteryid,model,set_moneys,):
    bet_list_flag = ''
    money_dict = dict()
    for i in range(10):
        money_dict[str(i)] = set_moneys[::-1]

    while(1):
        next_issue = getCurInfoAndModel(lotteryid, cookies)[0]
        numbs_dict = Get_last30_number(lotteryid, cookies)
        now_issue = '%0*d' % (4, int(next_issue.split('-')[1])-1)

        try:
            now_numbs = numbs_dict[now_issue].split(',')
        except KeyError:
            time.sleep(1)
            continue

        if(now_numbs == bet_list_flag):
            print(time.asctime(time.localtime(time.time())),lotteryid,
                '当前期号：', next_issue, '等待开奖中……')
            time.sleep(10)
            continue
        else:
            for n, i in enumerate(bet_list_flag):
                if i == now_numbs[n]:
                    money_dict[str(n)] = set_moneys[::-1]

        bet_list = list() #位置 投注内容 金额
        for n, i in enumerate(now_numbs):
            if(len(money_dict[str(n)]) == 0):
                money_dict[str(n)] = set_moneys[::-1]
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
            time.sleep(5)
            continue


if __name__ == "__main__":
    '''
        方案一：开什么投什么 
    '''
    print('钻石国际自动投注')
    print('方案一：开什么投什么')
    #lotteryid=input("输入彩种前的序号   22极速赛车        3幸运飞艇        31欢乐赛车：")
    print('22极速赛车        3幸运飞艇        31欢乐赛车')
    model=input('选择模式前的序号 1真实 2模拟：')
    set_moneys = input("输入投注金额（用空格分隔开）：").split(' ')
    cookies=login()

    p1=Process(target=worker1,args=(cookies,'22',model,set_moneys,))
    p2=Process(target=worker1,args=(cookies,'3',model,set_moneys,))
    p3=Process(target=worker1,args=(cookies,'31',model,set_moneys,))
    p1.start()
    p2.start()
    p3.start()
    
    input('123')