import os
from datetime import datetime
from time import sleep

import pytz
from okx.Trade import TradeAPI

# *************************************
#
# Не знаком с python-okx ?
# Посмотри базу
# https://www.youtube.com/playlist?list=PLWVnIRD69wY6fnQkxIpcB-K7R_AQuA3hT
# https://github.com/AzzraelCode/azzyt-okx
#
# *************************************
inst_id = "TRX-USDT"

def main():
    print("*** AZZYT OKX Place TP/SL ***")


    try:
        keys = dict(
            api_key=os.getenv('API_KEY'),
            api_secret_key=os.getenv('API_SECRET'),
            passphrase=os.getenv('API_PASSPHRASE'),
            flag='0', # Real
            debug=False,
        )

        cl = TradeAPI(**keys)
        # r = cl.place_order(
        #     instId=inst_id,
        #     tdMode='cash', # non margin
        #     side="buy",
        #     tgtCcy='base_ccy',
        #
        #     # ordType='market',
        #     ordType='limit',
        #     px='0.2902',
        #     sz=30,
        #     slTriggerPx='0.1',
        #     slOrdPx='-1',
        #     tpTriggerPx='0.5',
        #     tpOrdPx='-1',
        # )
        # print(r)

        # For placing order with TP/Sl:
        # 1. TP/SL algo order will be generated only when this order is filled fully, or there is no TP/SL algo order generated.
        # r = cl.get_order_list(instId=inst_id)

        # !!! Если при постановке лимитки ставим ТОЛЬКО SL или ТОЛЬКО TP то получим conditional
        # r = cl.order_algos_list(instId=inst_id, ordType='conditional')
        # !!! Если оба, то получим oco
        # r = cl.order_algos_list(instId=inst_id, ordType='oco')

        # когда лимитка наполняется - выпускается алго ордер со своим algoId и ordType
        r = cl.cancel_algo_order([dict(instId=inst_id, algoId='xxxxx')])
        print(r)

    except KeyboardInterrupt:
        print("Bye!")