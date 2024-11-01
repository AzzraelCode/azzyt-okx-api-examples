"""

    Другие видосы по Websocket OKX API
    https://www.youtube.com/watch?v=YCEMCVWiSH0

    Регистрация на OKX
    https://www.okx.com/join/AzzraelCode

    Спасибо автору
    https://azzrael.ru/spasibo

"""
import asyncio
import binascii
import json
import operator
import traceback

import httpx
import websockets

def print_ob(s, obs: dict, levels=10) -> None:
    """
    Выводим ближайшие к спреду неск уровней стакана
    :param levels:
    :param s:
    :param obs:
    :return:
    """
    print("\n", s)
    print("\n".join([f"{r[0]} {r[1]}" for r in sorted(obs['asks'], key=operator.itemgetter(0), reverse=True)[-1*levels:]]))
    print("-")
    print("\n".join([f"{r[0]} {r[1]}" for r in sorted(obs['bids'], key=operator.itemgetter(0), reverse=True)[:levels]]))


def update(s, data, ob: dict) -> dict:
    """
    Инкрементальное наполнение стакана
    :param s:
    :param data:
    :param ob:
    :return:
    """
    # ID связан с подпиской и символом, для каждого символа цепочка seqId своя !!!
    prev_seq_id = data[0].get("prevSeqId")
    if prev_seq_id != ob[s]['seqId']: raise Exception(f"{s} prevSeqId is not eq seqId")

    for k in ["asks", "bids"]:
        for v in data[0][k]:
            # !! важно для checksum - храним числа как строки
            price = v[0]
            vol = v[1]
            idx = next((idx for idx, val in enumerate(ob[s][k]) if price == val[0]), None)  # ищем индекс уровня цены

            if idx is None:
                # локально уровня нет
                ob[s][k].append([price, vol])
            elif vol == "0":
                # уровень есть, но объем ушел = удалить уровень
                del ob[s][k][idx]
            else:
                # объем на уровне изменился
                ob[s][k][idx][1] = vol


    ob[s]['seqId'] = data[0].get("seqId")

    print_ob(s, ob[s])
    checksum(s, ob[s], data[0].get("checksum"))
    return ob


def snapshot(s, data, ob: dict) -> dict:
    """
    Первоначальное наполнение стакана
    :param s:
    :param data:
    :param ob:
    :return:
    """
    ob[s] = {"asks": [], "bids": [], 'seqId': data[0].get("seqId")}
    for k in ["asks", "bids"]:
        # !! важно для checksum - храним числа как строки
        ob[s][k] = [ [l[0], l[1]] for l in data[0][k] ]

    print_ob(s, ob[s])
    checksum(s, ob[s], data[0].get("checksum"))

    return ob

def checksum(s, obs: dict, checksum_: int) -> bool:
    """  
    Проверка контрольной суммы стакана
    :param s:
    :param obs:
    :param checksum_: !!! signed CRC32
    :return:
    """
    asks = sorted(obs["asks"], key=lambda x: float(x[0]), reverse=False)[:25] # возрастание
    bids = sorted(obs["bids"], key=lambda x: float(x[0]), reverse=True)[:25] # убывание
    # print(bids, asks, sep="\n\n")
    crc_lst = [f"{bids[i][0]}:{bids[i][1]}:{asks[i][0]}:{asks[i][1]}" for i in range(len(asks))]
    crc_str = ":".join(crc_lst)
    crc = binascii.crc32(crc_str.encode()) # unsigned CRC32 !!!
    checksum_ = checksum_ & 0xffffffff # make unsigned CRC32 to compare
    # print(crc, checksum_)
    if not crc == checksum_:
        raise Exception(f"{s} checksum {crc} is not equal to {checksum_}")


async def loop():
    """
    Подключение и реконнекты к Websocket OKX API
    ! Функция асинхронная, для стакана это мб важно !
    :return:
    """
    ob = dict()
    url = "wss://ws.okx.com:8443/ws/v5/public"
    while True:
        try:
            async with websockets.connect(url) as ws:
                # * Оформляем подписку
                # https://www.okx.com/docs-v5/en/#order-book-trading-market-data-ws-order-book-channel
                # books = depth 400 @ 100ms, books5
                # tbt = delay 10ms vs 100ms on not tbt
                subs_args = [
                    dict(channel="books", instId="ALGO-USDT"),
                    dict(channel="books", instId="EOS-USDT"),
                    dict(channel="books", instId="BNB-USDT"),
                    # dict(channel="books5", instId="ETH-USDT-SWAP"),
                    # dict(channel="books5", instId="XRP-USDT-SWAP"),
                ]
                subs_msg = json.dumps(dict(op='subscribe', args=subs_args))
                await ws.send(subs_msg)

                # Получаем пуши
                async for p in ws:
                    p = json.loads(p)
                    ev = p.get("arg", {}).get("channel")
                    s = p.get("arg", {}).get("instId")

                    if ev == "books5":
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
                            print("\n".join([f"{r[0]:.4f} {r[1]:8.2f}" for r in t['asks'][:5]]))
                            print("-")
                            print("\n".join([f"{r[0]:.4f} {r[1]:8.2f}" for r in t['bids'][:5]]))
                            print("\n")

                    elif ev == "books":
                        data = p.get('data')
                        action = p.get('action')

                        if action == "snapshot": ob = snapshot(s, data, ob)
                        elif action == "update": ob = update(s, data, ob)

                    else:
                        print(p)


        except Exception as e:
            print(traceback.format_exc())

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
