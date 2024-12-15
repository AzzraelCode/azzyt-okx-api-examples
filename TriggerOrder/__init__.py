import os

from okx.Account import AccountAPI
from okx.Trade import TradeAPI


# *************************************
#
# Не знаком с python-okx ?
# Посмотри базу
# https://www.youtube.com/playlist?list=PLWVnIRD69wY6fnQkxIpcB-K7R_AQuA3hT
# https://github.com/AzzraelCode/azzyt-okx
#
# *************************************
def main():
    print("*** AZZYT OKX Trigger Order ***")
    try:
        keys = dict(
            api_key=os.getenv('API_KEY'),
            api_secret_key=os.getenv('API_SECRET'),
            passphrase=os.getenv('API_PASSPHRASE'),
            flag='0', # Real
            debug=False,
        )

        # api = AccountAPI(**keys)
        # print(api.get_account_balance())

        # r = TradeAPI(**keys).place_order(
        #     instId="TRX-USDT",
        #     tdMode='cash', # non margin
        #     side="buy",
        #     tgtCcy='base_ccy',
        #
        #     ordType='limit',
        #     px='0.2',
        #     sz=30,
        # )
        # print(r)

        # https://www.okx.com/docs-v5/en/#order-book-trading-algo-trading-post-place-algo-order
        r = TradeAPI(**keys).place_algo_order(
            instId="TRX-USDT",
            tdMode='cash', # non margin
            side="sell",
            tgtCcy='base_ccy',
            sz=30,

            ordType='trigger',
            triggerPx='0.5',
            orderPx='-1',
        )
        print(r)

    except KeyboardInterrupt:
        print("Bye!")