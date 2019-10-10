from fangan1 import *
from fangan2 import *
from fangan3 import *


if __name__ == "__main__":
    #一个方案一个进程
    multiprocessing.freeze_support()
    print('钻石国际自动投注')
    print('22极速赛车        3幸运飞艇        8疯狂赛车')
    cookies=login()
    #cookies=''
    #fangan2(cookies)
    p1=Process(target=fangan1,args=(cookies,))
    p2=Process(target=fangan2,args=(cookies,))
    p3=Process(target=fangan3,args=(cookies,))
    p1.start()
    p2.start()
    p3.start()