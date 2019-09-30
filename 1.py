import requests
import json

url = 'https://www.zs6606.com/index.html'
login_test_url = 'https://www.zs6606.com/login/testPlay.do'
login_url = 'https://www.zs6606.com/login/login.do'
bet_url = 'https://www.zs6606.com/lottery/bet.do'
curInfo_url='https://www.zs6606.com/lottery/getCurInfoAndModel.do'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',

}

'''
                    极速赛车        幸运飞艇        欢乐赛车
lotteryid           22                             31

1~10名methodid      1142                           4642
                    |                              |
                    1242                           4742       冠军『01』

冠亚组合methodid     1243                           4743
                    |                              |
                    1259                           4759       冠、亚军和『3』


'''
r = requests.post(login_test_url, headers=headers)
cookies = r.cookies

def getCurInfoAndModel(lotteryid,cookies):
    r=requests.post(curInfo_url,cookies=cookies,headers=headers,data={'lotteryid':str(lotteryid),'pageflag':'smp'})
    return r.text

def Bet(lotteryid, issue, method_list, cookies):
    '''
          彩种 期号 下注内容列表 cookies

          method_list[
              ['冠军','01',1],['冠亚军和','3',1]        #第一位，服务器无验证，但需要填入
          ]

    '''
    str_l = list()
    if str(lotteryid) == '22':
        methodid_start = [1142, 1243]          #[ 1~10 , 冠亚组合]
    elif str(lotteryid) == '31':
        methodid_start = [4642, 4743]

    for i in method_list:
        if(i[0] == '冠亚军和'):
            str_l.append(
                {
                    'methodid': str(int(methodid_start[1])+int(i[1])-3),
                    #'betcontent':'冠、亚军和『%s』' % i[1],
                    'amount':str(i[2])
                }
            )

        else:
            str_l.append(
                {
                    'methodid': str(int(methodid_start[0])+int(i[1])-1),
                    #'betcontent':'%s『%s』' % (i[0],i[1]),
                    'amount':str(i[2])
                }
            )

    data = {
        'lotteryid': str(lotteryid),  # "22"
        'issue': str(issue),  # '20190930-0127'
        'total': str(len(method_list)),  # "2"
        'list': str(str_l)                     # '''[{"methodid":"1142","betcontent":"冠军『01』","amount":"1"},{"methodid":"1233","betcontent":"第十名『01』","amount":"1"}]''',
    }
    r = requests.post(bet_url, headers=headers, data=data, cookies=cookies)
    print(r.text)



d=json.loads(getCurInfoAndModel(22,cookies))
curIssue=d['data']['curIssue']
Bet(22, curIssue,[['冠亚军和','19',1]], cookies)
input()
