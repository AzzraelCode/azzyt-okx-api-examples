"""

    Другие видосы по Websocket OKX API
    https://www.youtube.com/watch?v=YCEMCVWiSH0

    Регистрация на OKX
    https://www.okx.com/join/AzzraelCode

    Спасибо автору
    https://azzrael.ru/spasibo

"""
import asyncio
import json
import operator
import httpx
import websockets

async def loop():
    """
    Подключение и реконнекты к Websocket OKX API
    ! Функция асинхронная, для стакана это мб важно !
    :return:
    """
    url = "wss://ws.okx.com:8443/ws/v5/public"
    while True:
        try:
            async with websockets.connect(url) as ws:
                # * Оформляем подписку
                # https://www.okx.com/docs-v5/en/#order-book-trading-market-data-ws-order-book-channel
                # books = depth 400 @ 100ms, books5
                # tbt = delay 10ms vs 100ms on not tbt
                subs_args = [
                    dict(channel="books", instId="BTC-USDT-SWAP"),
                    # dict(channel="books5", instId="ETH-USDT-SWAP"),
                    # dict(channel="books5", instId="XRP-USDT-SWAP"),
                ]
                subs_msg = json.dumps(dict(op='subscribe', args=subs_args))
                await ws.send(subs_msg)

                # Получаем пуши
                async for p in ws:
                    p = json.loads(p)
                    ev = p.get("arg", {}).get("channel")
                    if ev == "books5":
                        s = p.get("arg", {}).get("instId")
                        data = p.get('data')

                        t = dict(asks=[], bids=[])
                        if data:
                            for k in ['asks', 'bids']:
                                t[k] = sorted(
                                    [[float(v[0]), float(v[1])] for v in data[0].get(k, [])],
                                    key=operator.itemgetter(0),
                                    reverse=True
                                )

                            # * выведем красиво
                            print(f"\n{s}")
                            print("\n".join([f"{r[0]:.4f} {r[1]:8.2f}" for r in t['asks']]))
                            print("-")
                            print("\n".join([f"{r[0]:.4f} {r[1]:8.2f}" for r in t['bids']]))
                            print("\n")
                    else:
                        print(p)


        except Exception as e:
            print(e)

        await asyncio.sleep(5)

def get_orderbook():
    """
    Порлучение стаканов через REST OKX API
    https://www.okx.com/docs-v5/en/#order-book-trading-market-data-get-order-book
    https://www.okx.com/docs-v5/en/#order-book-trading-market-data-get-full-order-book
    :return:
    """
    # url = "https://www.okx.com/api/v5/market/books"
    url = "https://www.okx.com/api/v5/market/books-full"
    r = httpx.get(url, params=dict(instId="BTC-USDT-SWAP", sz=10))
    print(r.json())


def main():
    print("*** AZZYT OKX Websocket Orderbook ***")
    try:
        asyncio.run(loop())
    except KeyboardInterrupt:
        ...
