from import_functions_define import *

def worker1(cookies,lotteryid,model,stop_to_bet,set_moneys,chedao,treeview1,treeview2,balance_label,zongshuying_label):
    '''
    方案一主函数 。单参数有多个值的均为列表
    '''
    bet_list_flag = ''
    money_dict = dict()
    for i in range(10):
        money_dict[str(i)] = set_moneys[::-1]

    bet_list_dict=dict()
    bet_location_dict=dict()        #每个位置 正在下注的数字
    for i in range(10):
        bet_location_dict[str(i)]=dict()

    while(1):
        try:
            next_issue = getCurInfoAndModel(lotteryid, cookies)[0]
            numbs_dict = Get_last30_number(lotteryid, cookies)
            if(lotteryid=='9'):
                now_issue=str(int(next_issue[-4:])-1)
            else:
                now_issue = '%0*d' % (4, int(next_issue.split('-')[1])-1)  #仅4位
            treeview_del(treeview1)
            treeview_insert(treeview1,numbs_dict)          #设置开奖信息
            balance_label.set(GetUserBalance(cookies))     #设置余额
        except:
            #print(traceback.print_exc())
            print('获取账户信息失败，等待10秒后重试')
            time.sleep(10)
            continue
            
        zong=0
         #计算彩种总输赢
        for i in bet_list_dict:
            for u in bet_list_dict[i]:
                try:
                    if(lotteryid=='9'):
                        if(u[1]==numbs_dict[i[-4:]].split(',')[int(u[0])]):
                            zong+=int(u[2])*9.96-int(u[2])
                        else:
                            zong-=int(u[2])
                    else:
                        if(u[1]==numbs_dict[i.split('-')[1]].split(',')[int(u[0])]) :
                            zong+=int(u[2])*9.96-int(u[2])
                        else:
                            zong-=int(u[2])
                except:
                    #print('计算输赢金额出错')
                    pass

        if(int(zong)>=int(stop_to_bet[0])):
            input("止赢，等待中……")
        elif(int(zong)<=-int(stop_to_bet[1])):
            input("止损，等待中……")
    
        if(model=='1'):
            try:
                zongshuying_label.set(ZongWinSearch(cookies))  #设置今日总输赢
            except:
                pass
        else:
            #单彩种总输赢
            zongshuying_label.set(str(zong))

        try:
            now_numbs = numbs_dict[now_issue].split(',')
        except KeyError:
            print('彩种：%s' % lotteryid,'开奖结果尚未更新，正在重试……')
            time.sleep(10)
            continue

        if(now_numbs == bet_list_flag):
            print(time.asctime(time.localtime(time.time())),lotteryid,
                '当前期号：', next_issue, '等待开奖中……')
            time.sleep(10)
            continue
        else:
            if(lotteryid=='9'):
                last_numbs=numbs_dict[str(int(now_issue)-1)] .split(',')            
            else:
                last_numbs= numbs_dict['%0*d' % (4, int(now_issue)-1)] .split(',')
            #验证是否中奖
            for i in bet_location_dict:
                if(now_numbs[int(i)] in bet_location_dict[i] and len(bet_location_dict[i][now_numbs[int(i)]])!=0):
                    print(now_issue,i,now_numbs[int(i)],'中奖')
                    bet_location_dict[i][now_numbs[int(i)]]=list()
            for n,i in enumerate(now_numbs):
                if(i==last_numbs[n]):
                    #money_dict[str(n)]=set_moneys[::-1]
                    bet_location_dict[str(n)][i]=set_moneys[::-1]               #设置金额。bet_location_dict[赛道][数字]=金额列表

            '''for n, i in enumerate(bet_list_flag):
                if i == now_numbs[n]:
                    money_dict[str(n)] = set_moneys[::-1]'''

        bet_list = list() #位置 投注内容 金额
        for i in bet_location_dict:
            if(str(i) not in chedao):
                continue
            if(len(bet_location_dict[i])!=0):
                for u in bet_location_dict[i]:
                    if(len(bet_location_dict[i][u])!=0):
                        bet_money=str(bet_location_dict[i][u].pop())
                        bet_list.append([str(i), u, bet_money])

        bet_list_dict[next_issue]=bet_list

        treeview_del(treeview2)
        treeview2_insert(treeview2,bet_list_dict)          #设置投注信息

        if(len(bet_list)!=0):
            if(model=='1'):
                try:
                    if(str(lotteryid)=='3'):
                        d = Bet(lotteryid, ''.join(next_issue.split('-')), bet_list, cookies)
                    else:
                        d = Bet(lotteryid, next_issue, bet_list, cookies)
                except:
                    d='0'
                    print("投注异常")
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
            if(d != '200'):
                print('投注失败，跳过')
                print(d)
                time.sleep(10)
        bet_list_flag = now_numbs[:]

def fangan1(cookies):
    #方案一 主线程
    base=tk.Tk()
    base.title('方案一：开什么投什么 qq792301982')
    base.geometry('760x700')

    fm1=Frame(base)
    balance_label = StringVar()
    balance_label.set('0')
    Label(fm1, text='余额：').grid(row=1,column=1)
    Label(fm1, textvariable=balance_label).grid(row=1,column=2)
    zongshuying_label=StringVar()
    zongshuying_label.set('0')
    Label(fm1, text='今日总输赢：').grid(row=2,column=1)
    Label(fm1, textvariable=zongshuying_label).grid(row=2,column=2)
    fm1.grid(row=1,column=1)

    def start_bet(frame,cookies,lotteryid,model,stop_to_bet,set_moneys,chedao,treeview1,treeview2,balance_label,zongshuying_label):
        t=threading.Thread(target=worker1,args=(cookies,lotteryid,model,stop_to_bet,set_moneys,chedao,treeview1,treeview2,balance_label,zongshuying_label,))
        t.start()
        def pause_bet():
            print('暂停')
            stop_thread(t)
        Button(frame,text="暂停",command=pause_bet).grid(row=13,column=1)

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

    columns=['期号','赛道','投注内容','投注金额']
    treeview_jisu2 =ttk.Treeview(frame1, height=10, show="headings", columns=columns)  # 表格
    treeview_jisu2.column("期号", width=100, anchor='center') # 表示列,不显示
    treeview_jisu2.column("赛道", width=30, anchor='center')
    treeview_jisu2.column("投注内容", width=50, anchor='center')
    treeview_jisu2.column("投注金额", width=50, anchor='center')
    treeview_jisu2.heading("期号", text="期号") # 显示表头
    treeview_jisu2.heading("赛道", text="赛道")
    treeview_jisu2.heading("投注内容", text="投注内容")
    treeview_jisu2.heading("投注金额", text="投注金额")
    treeview_jisu2.grid(row=2,column=col+1)

    Label(frame1, text="极速赛车止赢止损（空格分隔）：").grid(row=4,column=col)
    text_jisu_stop2bet=Text(frame1,width=10,height=2)
    text_jisu_stop2bet.grid(row=5,column=col)

    Label(frame1, text="极速赛车模式（1真实 2模拟）：").grid(row=6,column=col)
    text_jisu_model=Text(frame1,width=10,height=2)
    text_jisu_model.grid(row=7,column=col)

    Label(frame1, text="极速赛车金额（空格分隔）：").grid(row=8,column=col)
    text_jisu_moneys=Text(frame1,width=20,height=4)
    text_jisu_moneys.grid(row=9,column=col)

    Label(frame1, text="极速赛车车道（空格分隔）0代表第一名 1代表第二名…… 9代表第十名：").grid(row=10,column=col)
    text_jisu_chedao=Text(frame1,width=10,height=2)
    text_jisu_chedao.grid(row=11,column=col)

    Button(frame1,text="开始",command=lambda:start_bet(frame1,cookies,'22',text_jisu_model.get('1.0',END).strip(),text_jisu_stop2bet.get('1.0',END).strip().split(' '),text_jisu_moneys.get('1.0',END).strip().split(' '),text_jisu_chedao.get('1.0',END).strip().split(' '),treeview_jisu1,treeview_jisu2,balance_label,zongshuying_label)).grid(row=12,column=col)


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

    columns=['期号','赛道','投注内容','投注金额']
    treeview_xingyun2 =ttk.Treeview(frame2, height=10, show="headings", columns=columns)  # 表格
    treeview_xingyun2.column("期号", width=100, anchor='center') # 表示列,不显示
    treeview_xingyun2.column("赛道", width=30, anchor='center')
    treeview_xingyun2.column("投注内容", width=50, anchor='center')
    treeview_xingyun2.column("投注金额", width=50, anchor='center')
    treeview_xingyun2.heading("期号", text="期号") # 显示表头
    treeview_xingyun2.heading("赛道", text="赛道")
    treeview_xingyun2.heading("投注内容", text="投注内容")
    treeview_xingyun2.heading("投注金额", text="投注金额")
    treeview_xingyun2.grid(row=2,column=col+1)

    Label(frame2, text="feiting止赢止损（空格分隔）：").grid(row=4,column=col)
    text_feiting_stop2bet=Text(frame2,width=10,height=2)
    text_feiting_stop2bet.grid(row=5,column=col)

    Label(frame2, text="feiting模式（1真实 2模拟）：").grid(row=6,column=col)
    text_feiting_model=Text(frame2,width=10,height=2)
    text_feiting_model.grid(row=7,column=col)

    Label(frame2, text="feiting金额（空格分隔）：").grid(row=8,column=col)
    text_feiting_moneys=Text(frame2,width=20,height=4)
    text_feiting_moneys.grid(row=9,column=col)

    Label(frame2, text="feiting车道（空格分隔）0代表第一名 1代表第二名…… 9代表第十名：").grid(row=10,column=col)
    text_feiting_chedao=Text(frame2,width=10,height=2)
    text_feiting_chedao.grid(row=11,column=col)

    Button(frame2,text="开始",command=lambda:start_bet(frame2,cookies,'3',text_feiting_model.get('1.0',END).strip(),text_feiting_stop2bet.get('1.0',END).strip().split(' '),text_feiting_moneys.get('1.0',END).strip().split(' '),text_feiting_chedao.get('1.0',END).strip().split(' '),treeview_xingyun1,treeview_xingyun2,balance_label,zongshuying_label)).grid(row=12,column=col)

    #9疯狂赛车
    col=3
    frame3=Frame(notebook)
    Label(frame3, text="9疯狂赛车开奖信息：").grid(row=1,column=col)
    columns=['期号','开奖号']
    treeview_fengkuang1 =ttk.Treeview(frame3, height=10, show="headings", columns=columns)  # 表格
    treeview_fengkuang1.column("期号", width=50, anchor='center') # 表示列,不显示
    treeview_fengkuang1.column("开奖号", width=200, anchor='center')
    treeview_fengkuang1.heading("期号", text="期号") # 显示表头
    treeview_fengkuang1.heading("开奖号", text="开奖号")
    treeview_fengkuang1.grid(row=2,column=col)

    columns=['期号','赛道','投注内容','投注金额']
    treeview_fengkuang2 =ttk.Treeview(frame3, height=10, show="headings", columns=columns)  # 表格
    treeview_fengkuang2.column("期号", width=100, anchor='center') # 表示列,不显示
    treeview_fengkuang2.column("赛道", width=30, anchor='center')
    treeview_fengkuang2.column("投注内容", width=50, anchor='center')
    treeview_fengkuang2.column("投注金额", width=50, anchor='center')
    treeview_fengkuang2.heading("期号", text="期号") # 显示表头
    treeview_fengkuang2.heading("赛道", text="赛道")
    treeview_fengkuang2.heading("投注内容", text="投注内容")
    treeview_fengkuang2.heading("投注金额", text="投注金额")
    treeview_fengkuang2.grid(row=2,column=col+1)

    Label(frame3, text="fengkuang止赢止损（空格分隔）：").grid(row=4,column=col)
    text_fengkuang_stop2bet=Text(frame3,width=10,height=2)
    text_fengkuang_stop2bet.grid(row=5,column=col)

    Label(frame3, text="fengkuang模式（1真实 2模拟）：").grid(row=6,column=col)
    text_fengkuang_model=Text(frame3,width=10,height=2)
    text_fengkuang_model.grid(row=7,column=col)

    Label(frame3, text="fengkuang金额（空格分隔）：").grid(row=8,column=col)
    text_fengkuang_moneys=Text(frame3,width=20,height=4)
    text_fengkuang_moneys.grid(row=9,column=col)

    Label(frame3, text="fengkuang车道（空格分隔）0代表第一名 1代表第二名…… 9代表第十名：").grid(row=10,column=col)
    text_fengkuang_chedao=Text(frame3,width=10,height=2)
    text_fengkuang_chedao.grid(row=11,column=col)

    Button(frame3,text="开始",command=lambda:start_bet(frame3,cookies,'9',text_fengkuang_model.get('1.0',END).strip(),text_fengkuang_stop2bet.get('1.0',END).strip().split(' '),text_fengkuang_moneys.get('1.0',END).strip().split(' '),text_fengkuang_chedao.get('1.0',END).strip().split(' '),treeview_fengkuang1,treeview_fengkuang2,balance_label,zongshuying_label)).grid(row=12,column=col)

    notebook.add(frame1, text="22极速赛车")
    notebook.add(frame2, text="3幸运飞艇")
    notebook.add(frame3, text="9疯狂赛车")
    notebook.grid(row=1,column=2)
    
    base.mainloop()

if __name__ == "__main__":
    #一个方案一个进程
    multiprocessing.freeze_support()
    '''
        方案一：开什么投什么 
    '''
    print('钻石国际自动投注')
    print('方案一：开什么投什么')
    print('22极速赛车        3幸运飞艇        9疯狂赛车')

    cookies=login()
    #cookies=''
    fangan1(cookies)
    # p1=Process(target=worker1,args=(cookies,'22',model,set_moneys,jisusaiche_chedao,))
    # p2=Process(target=worker1,args=(cookies,'31',model,set_moneys,fengkuang_chedao,))
    # p1.start()
    # p2.start()