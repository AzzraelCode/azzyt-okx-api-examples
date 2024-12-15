import os
from datetime import datetime
from time import sleep

import pytz
from okx.MarketData import MarketAPI

# *************************************
#
# Не знаком с python-okx ?
# Посмотри базу
# https://www.youtube.com/playlist?list=PLWVnIRD69wY6fnQkxIpcB-K7R_AQuA3hT
# https://github.com/AzzraelCode/azzyt-okx
#
# *************************************
inst_id = "BTC-USDT"
tf = '3Mutc'
limit = 20

def from_str_ms(time : str) -> datetime:
    return datetime.fromtimestamp(int(time) / 1000, tz=pytz.UTC)

def main():
    print("*** AZZYT OKX Candles History ***")
    candles = {}

    try:
        cl = MarketAPI(
            flag="0", # Real
            debug=True
        )

        for page in range(0, 10000):
            open_times = sorted([*candles.keys()])

            # https://www.okx.com/docs-v5/en/#order-book-trading-market-data-get-candlesticks
            r = cl.get_history_candlesticks(
                instId=inst_id,
                bar=tf,
                limit=limit,
                after=open_times[0] if len(open_times) > 0 else '',
            )
            # print(r)
            data = r.get('data', [])

            for c in data:
                candles[int(c[0])] = dict(
                    t=from_str_ms(c[0]),
                    x=c[0],
                    o=float(c[1]),
                    h=float(c[2]),
                    l=float(c[3]),
                    c=float(c[4]),
                    v=float(c[7])
                )

            # получили меньше чем могли, соотв на след странице ничего нет
            if len(data) < limit:
                print(f"Finished at page {page}")
                break

            # задержка чтобы не нарушать лимиты
            if page > 0 and page % 20 == 0:
                print(f"page {page}, safety delay...")
                sleep(2)

        # вывод для ролика
        [print(f"{c['t']} | {c['x']} | {c['o']:>12.2f}") for c in candles.values()]


    except KeyboardInterrupt:
        print("Bye!")