import asyncio
import numpy as np
import time

class Strats:

    current_position = 'neutral'
    trade_begin_time = int(time.time())

    trade_pause = 0
    base_qty = 10

    # Compared RSI based on index price and mark price, can either go long, short, or stay neutral
    async def strategyOne(self, ws, tick, rsi, bidwall, askwall):
        
        if self.current_position == 'long':
            if rsi['mark_price'] < 32 and rsi['index_price'] < 35:
                print('\n\nClose Long *ta: {} {} {}'.format(tick['best_bid_price'][0], tick['best_ask_price'][0], tick['mark_price'][0]))

                await self.api.cancel_all(ws)
                await asyncio.sleep(0.3)
                await self.api.sell(ws, "BTC-PERPETUAL", self.base_qty, round(float(tick["best_ask_price"][0]) - 1, 2))

                self.current_position = 'neutralx'
                self.trade_begin_time = int(time.time())
                self.trade_pause = int(time.time())

            elif self.api.db.order_totals['Filled Ask'] == self.base_qty:
                print('\n\nClose Long *tc: {} {} {}'.format(tick['best_bid_price'][0], tick['best_ask_price'][0], tick['mark_price'][0]))

                self.current_position = 'neutralx'
                self.trade_begin_time = int(time.time())
                self.trade_pause = int(time.time())

            elif int(time.time()) - self.trade_begin_time > 30:
                print('\n\nClose Long *tb: {} {} {}'.format(tick['best_bid_price'][0], tick['best_ask_price'][0], tick['mark_price'][0]))

                await self.api.cancel_all(ws)
                await asyncio.sleep(0.3)
                await self.api.sell(ws, "BTC-PERPETUAL", self.base_qty, round(float(tick["best_ask_price"][0]) - 1, 2))

                self.current_position = 'neutralx'
                self.trade_begin_time = int(time.time())
                self.trade_pause = int(time.time())

            else:
                pass


        if self.current_position == 'short':
            if rsi['mark_price'] > 65 and rsi['index_price'] > 62:
                print('\n\nClose Short: {} {} {} *ta'.format(tick['best_bid_price'][0], tick['best_ask_price'][0], tick['mark_price'][0]))

                await self.api.cancel_all(ws)
                await asyncio.sleep(0.3)
                await self.api.buy(ws, "BTC-PERPETUAL", self.base_qty, round(float(tick["best_bid_price"][0]) + 1, 2))

                self.current_position = 'neutralx'
                self.trade_begin_time = int(time.time())
                self.trade_pause = int(time.time())

            elif self.api.db.order_totals['Filled Bid'] == self.base_qty:
                print('\n\nClose Short: {} {} {} *tc'.format(tick['best_bid_price'][0], tick['best_ask_price'][0], tick['mark_price'][0]))

                self.current_position = 'neutralx'
                self.trade_begin_time = int(time.time())
                self.trade_pause = int(time.time())

            elif int(time.time()) - self.trade_begin_time > 30:
                print('\n\nClose Short: {} {} {} *tb'.format(tick['best_bid_price'][0], tick['best_ask_price'][0], tick['mark_price'][0]))

                await self.api.cancel_all(ws)
                await asyncio.sleep(0.3)
                await self.api.buy(ws, "BTC-PERPETUAL", self.base_qty, round(float(tick["best_bid_price"][0]) + 1, 2))


                self.current_position = 'neutralx'
                self.trade_begin_time = int(time.time())
                self.trade_pause = int(time.time())

            else:
                pass


        if self.current_position == 'neutral':
            #if rsi['mark_price'] > 80 and rsi['index_price'] > 80:
            if rsi['mark_price'] > 70 and rsi['index_price'] > 65 and askwall < 0.177 and bidwall > 0.1977:
                print('\n\nEnter Long: {} {} {} {} {}'.format(tick['best_bid_price'][0], tick['best_ask_price'][0], tick['mark_price'][0], bidwall, askwall))

                await self.api.buy(ws, "BTC-PERPETUAL", self.base_qty, round(float(tick["best_bid_price"][0]) + 1.5, 2))
                await asyncio.sleep(1)
                await self.api.sell(ws, "BTC-PERPETUAL", self.base_qty, round(float(tick["best_ask_price"][0]) + 3.5, 2))

                self.current_position = 'long'
                self.trade_begin_time = int(time.time())

            #if rsi['mark_price'] < 20 and rsi['index_price'] < 20:
            if rsi['mark_price'] < 30 and rsi['index_price'] < 35 and bidwall < 0.177 and askwall > 0.1977:
                print('\n\nEnter Short: {} {} {} {} {}'.format(tick['best_bid_price'][0], tick['best_ask_price'][0], tick['mark_price'][0], bidwall, askwall))

                await self.api.sell(ws, "BTC-PERPETUAL", self.base_qty, round(float(tick["best_ask_price"][0]) - 1.5, 2))
                await asyncio.sleep(1)
                await self.api.buy(ws, "BTC-PERPETUAL", self.base_qty, round(float(tick["best_bid_price"][0]) - 3.5, 2))


                self.current_position = 'short'
                self.trade_begin_time = int(time.time())


        if self.current_position == 'neutralx':
            self.api.db.order_cache = {}
            if int(time.time()) - self.trade_pause > 10:
                self.current_position = 'neutral'
                self.trade_pause = int(time.time())
