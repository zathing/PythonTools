# -*- coding: utf-8 -*-
import datetime
import ystockquote
from threading import Thread
# from multiprocessing import Process


# 仙人指路
def xrzl(stockid):
    now_format = datetime.datetime.now().strftime('%Y%m%d|%H%M%S|%w').split('|')
    now_date = int(now_format[0])
    now_week = int(now_format[2])

    if now_week == 0:
        begin = now_date - 4
        mid = now_date - 3
        end = now_date - 2
    elif now_week == 1:
        begin = now_date - 5
        mid = now_date - 4
        end = now_date - 3
    elif now_week == 2:
        begin = now_date - 5
        mid = now_date - 4
        end = now_date - 1
    elif now_week == 3:
        begin = now_date - 5
        mid = now_date - 2
        end = now_date - 1
    elif now_week == 4 or now_week == 5 or now_week == 6:
        begin = now_date - 3
        mid = now_date - 2
        end = now_date - 1

    begin = str(begin)
    mid = str(mid)
    end = str(end)

    begin = begin[:4] + '-' + begin[4:6] + '-' + begin[6:8]
    mid = mid[:4] + '-' + mid[4:6] + '-' + mid[6:8]
    end = end[:4] + '-' + end[4:6] + '-' + end[6:8]

    try:
        d = ystockquote.get_historical_prices(stockid, begin, end)
        if float(d[end]['Close']) > max(float(d[begin]['Open']), float(d[begin]['Close'])) and float(d[end]['Close']) > max(float(d[mid]['Open']), float(d[mid]['Close'])):
            for i in (begin, mid):
                up = float(d[i]['High']) - max(float(d[i]['Open']), float(d[i]['Close']))
                shi = abs(float(d[i]['Open']) - float(d[i]['Close']))
                down = abs(min(float(d[i]['Open']), float(d[i]['Close'])) - float(d[i]['Low']))
                if up > 3 * shi and up > 3 * down:
                    print stockid
    except:
        pass


# 缩量反转
def slfz(stockid):
    end = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    begin = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime('%Y-%m-%d')

    try:
        data = ystockquote.get_historical_prices(stockid, begin, end)
        volumes = []
        for d in data:
            volumes.append(int(data[d]['Volume']))
        if int(data[end]['Volume']) != 0 and int(data[end]['Volume']) == min(volumes):
            print stockid
    except:
        pass

if __name__ == "__main__":
    with open('./stocks.txt', 'r') as fo:
        for l in fo.readlines():
            # stock_process1 = Process(target=xrzl, args=(l.strip(),))
            # stock_process2 = Process(target=slfz, args=(l.strip(),))
            # stock_process1.start()
            # stock_process2.start()
            stock_thread1 = Thread(target=xrzl, args=(l.strip(),))
            stock_thread2 = Thread(target=slfz, args=(l.strip(),))
            stock_thread1.start()
            stock_thread2.start()
    print("done")
