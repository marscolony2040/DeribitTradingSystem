import numpy as np
import pandas as pd

from api import API
from strats import Strats

import asyncio
import websockets
import json
import time
import datetime

class Fetcher:

    # Cuts the orderbook to an inputted limit
    async def get_book(self, tag, limit):
        bp = self.api.db.bids[tag]['Price'].values[:limit].tolist()
        bv = self.api.db.bids[tag]['Volume'].values[:limit].tolist()
        ap = self.api.db.asks[tag]['Price'].values[:limit].tolist()
        av = self.api.db.asks[tag]['Volume'].values[:limit].tolist()
        return [bp, bv], [ap, av]

    # Returns a pandas dataframe of the orderbook
    async def get_ticker(self, tag, limit=None):
        if limit:
            return pd.DataFrame(data=list(reversed(self.api.db.tickerbook[tag].values[-limit:].tolist())), columns=self.api.db.tick_items)
        else:
            return pd.DataFrame(data=list(reversed(self.api.db.tickerbook[tag].values.tolist())), columns=self.api.db.tick_items)

    # Waits till orderbook has synced
    async def load_data(self, wait=30):
        while self.api.db.booksync == False:
            await asyncio.sleep(0.0001)
        t0 = await self.api.now()
        t1 = t0
        print('Loading DataFeed: ')
        while t1 - t0 <= wait*1000:
            t1 = await self.api.now()
            print('{}\t'.format('{0:.2f}'.format(int(t1 - t0)/1000)))
            await asyncio.sleep(1)
        print(': Finished Loading........\n\n')


class Misc(Fetcher):

    async def dfm(self, h):
        return '${0:.2f}'.format(h)


class System(Misc, Strats):

    def __init__(self, key, secret, channels):
        self.api = API(key, secret, channels)
        self.opened = False

    # Subscribes to the two clients and outputter
    async def start(self, wss):
        async with websockets.connect(self.api.url) as ws:
            await asyncio.wait([asyncio.ensure_future(self.dataClient(ws)),
                                asyncio.ensure_future(self.accountClient(ws)),
                                asyncio.ensure_future(self.outputReact(wss))])

    # Sends data to react.js front end to plot and place trading metrics
    async def outputReact(self, wss):
        await self.load_data()
        self.opened = True
        while self.api.db.booksync:
            try:
                bids, asks = await self.get_book("BTC-PERPETUAL", 15)
                tick = await self.get_ticker("BTC-PERPETUAL", limit=100)

                bW, sW = await self.api.db.check_for_walls(bids, asks)
                T = await self.api.db.prepare_orderbook_for_app(bids, asks)
                rsi = await self.api.db.rsi(tick)

                msg = {'Ticker':{
                                    'Timestamp': datetime.datetime.fromtimestamp(int(tick['timestamp'][0]/1000)).strftime('%m-%d-%Y %H:%M:%S'),
                                    'Mark Price': await self.dfm(tick['mark_price'][0]),
                                    'Index Price': await self.dfm(tick['index_price'][0]),
                                    'Bid Price': await self.dfm(tick['best_bid_price'][0]),
                                    'Ask Price': await self.dfm(tick['best_ask_price'][0]),
                                    'Last Price': await self.dfm(tick['last_price'][0])
                                },
                        'Metrics':{
                                    'Bid Wall Strength': '{0:.2f}%'.format(bW*100),
                                    'Ask Wall Strength': '{0:.2f}%'.format(sW*100),
                                    'Mark RSI': '{0:.2f}'.format(rsi['mark_price']),
                                    'Index RSI': '{0:.2f}'.format(rsi['index_price']),
                                    'Last RSI': '{0:.2f}'.format(rsi['last_price']),
                                    'Volatility': '${0:.2f}'.format(float(np.std(tick['mark_price'])))
                                },
                        'Book': T,
                        'Account': self.api.db.acct_sum,
                        'Orders': self.api.db.order_totals # Open Buy | Open Sell | Filled Buy | Filled Sell
                        }

                await wss.send(json.dumps(msg))
            except Exception as e:
                print('React Error: {}'.format(e))
            await asyncio.sleep(0.0347)

    # Manages account for trading strategy
    async def accountClient(self, ws):
        await asyncio.sleep(3)
        dt = int(time.time())
        while True:
            try:
                # Account Refresh Function
                if int(time.time()) - dt > 7:
                    await self.api.get_account_summary(ws)
                    await asyncio.sleep(0.27)
                    dt = int(time.time())


                # Trading Strategies Function
                if self.opened == True:
                    tick = await self.get_ticker("BTC-PERPETUAL", limit=100)
                    rsi = await self.api.db.rsi(tick)

                    bids, asks = await self.get_book("BTC-PERPETUAL", 15)
                    bW, sW = await self.api.db.check_for_walls(bids, asks)

                    #await self.strategyOne(ws, tick, rsi, bW, sW)


                # Update Order States
                try:
                    for v in self.api.db.order_cache:
                        await self.api.get_state(ws, v)
                        await asyncio.sleep(0.27)
                except:
                    pass

            except Exception as e:
                print('Account Error: {}'.format(e))

            await asyncio.sleep(0.001)

    # Retrieves the ticker feed and orderbook
    async def dataClient(self, ws):
        await self.api.public_auth(ws)
        await self.api.private_subscribe(ws)
        ii = 0
        while True:
            try:
                msg = json.loads(await ws.recv())
                k = msg.keys()
                if 'params' in k:
                    channel = msg['params']['channel']
                    if 'data' in msg['params'].keys():
                        data = msg['params']['data']
                        raw = channel.split('.')
                        if raw[0] == 'ticker':
                            await self.api.db.ticker(data, raw)
                        if raw[0] == 'book':
                            await self.api.db.orderbook(data, raw)
                elif 'id' in k:
                    await self.api.db.account(msg)
                else:
                    pass
            except Exception as e:
                #print("Data Error: {}".format(e))
                pass
