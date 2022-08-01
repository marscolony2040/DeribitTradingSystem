import numpy as np
import pandas as pd
import time
import datetime

class Model:

    # Returns current date stamp
    async def currentstamp(self):
        return datetime.datetime.fromtimestamp(int(time.time())).strftime('%m-%d-%Y %H:%M:%S')

    # Calculates RSI
    async def rsi(self, msg, targets=['mark_price', 'last_price', 'index_price']):
        async def calculate(v):
            u = np.sum([a - b for a, b in zip(v[:-1], v[1:]) if a - b >= 0])
            d = np.sum([abs(a - b) for a, b in zip(v[:-1], v[1:]) if a - b < 0])
            c = u/d if d != 0 else u/1
            return 100 - 100 / (1 + c)

        res = {}
        for i in targets:
            res[i] = await calculate(msg[i])
        return res

    # Checks for buy or sell walls
    async def check_for_walls(self, bids, asks, pct=0.25, stop=0.3):
        vB, vA = [bb for bb in bids[1]], [aa for aa in asks[1]]
        nB, nA = int(pct*len(vB)), int(pct*len(vA))
        sB, sA = np.sum(vB[:nB]), np.sum(vA[:nA])
        return sB / np.sum(vB[nB:]), sA / np.sum(vA[nA:])

    # Prepares orderbook to be sent to react.js app
    async def prepare_orderbook_for_app(self, bids, asks):
        n = len(bids[1])
        b, a, m = [], [], []
        for i in range(n):
            m.append(i)
            b.append(np.sum(bids[1][:i+1]))
            a.append(np.sum(asks[1][:i+1]))
        b = list(reversed(b))
        bids = ['${0:.2f}'.format(j) for j in list(reversed(bids[0]))]
        asks = ['${0:.2f}'.format(j) for j in asks[0]]
        return m, bids, asks, b, a

class Database(Model):

    def __init__(self, parent):
        self.parent = parent
        self.bids = {}
        self.asks = {}
        self.tickerbook = {}
        self.acct_sum = {}

        self.data_limit = 3000
        self.data_shave = 100

        self.tick_limit = 500
        self.tick_shave = 50

        self.booksync = False

        self.order_cache = {}

        self.tick_items = ('timestamp','mark_price','last_price','index_price','best_bid_price','best_ask_price')
        self.orderstash = ('Timestamp', 'Open Buy', 'Open Sell', 'Filled Buy', 'Filled Sell')
        self.order_totals = {'Open Bid': 0, 'Open Ask': 0, 'Filled Bid': 0, 'Filled Ask': 0}

        self.ok_to_update_order = True
        self.chaching = False

    # Takes a look at your account
    async def account(self, msg):
        idv = msg['id']

        if idv == 2515:
            for o in ('balance', 'available_funds', 'equity','session_upl','session_rpl'):
                self.acct_sum[o] = msg['result'][o]
        if idv == 1953:
            print(msg, end='\n\n')
        if idv == 5275:
            ord_id = msg['result']['order']['order_id']
            if ord_id not in self.order_cache.keys():
                self.order_cache[ord_id] = {'side':'buy', 'price': msg['result']['order']['price'], 'amount': msg['result']['order']['amount'], 'filled': msg['result']['order']['filled_amount']}
            else:
                self.order_cache[ord_id]['amount'] = msg['result']['order']['amount']
                self.order_cache[ord_id]['filled'] = msg['result']['order']['filled_amount']
                if self.order_cache[ord_id]['amount'] - self.order_cache[ord_id]['filled'] <= 0.00001:
                    del self.order_cache[ord_id]


        if idv == 5276:
            ord_id = msg['result']['order']['order_id']
            if ord_id not in self.order_cache.keys():
                self.order_cache[ord_id] = {'side':'sell', 'price': msg['result']['order']['price'], 'amount': msg['result']['order']['amount'], 'filled': msg['result']['order']['filled_amount']}
            else:
                self.order_cache[ord_id]['amount'] = msg['result']['order']['amount']
                self.order_cache[ord_id]['filled'] = msg['result']['order']['filled_amount']
                if self.order_cache[ord_id]['amount'] - self.order_cache[ord_id]['filled'] <= 0.00001:
                    del self.order_cache[ord_id]


        if idv == 3725:
            ord_id = msg['result']['order']['order_id']
            self.order_cache[ord_id]['price'] = msg['result']['order']['price']
            self.order_cache[ord_id]['amount'] = msg['result']['order']['amount']
            self.order_cache[ord_id]['filled'] = msg['result']['order']['filled_amount']
        if idv == 4214:
            ord_id = msg['result']['order_id']
            del self.order_cache[ord_id]

        self.order_totals = {'Open Bid': 0, 'Open Ask': 0, 'Filled Bid': 0, 'Filled Ask': 0}
        for oid in self.order_cache:
            if self.order_cache[oid]['side'] == 'buy':
                self.order_totals['Open Bid'] += (self.order_cache[oid]['amount'] - self.order_cache[oid]['filled'])
                self.order_totals['Filled Bid'] += self.order_cache[oid]['filled']
            else:
                self.order_totals['Open Ask'] += (self.order_cache[oid]['amount'] - self.order_cache[oid]['filled'])
                self.order_totals['Filled Ask'] += self.order_cache[oid]['filled']

    # Manages your ticker data
    async def ticker(self, msg, raw):
        channel = raw[1]
        if channel not in self.tickerbook.keys():
            self.tickerbook[channel] = pd.DataFrame(data=[[msg[i] for i in self.tick_items]], columns=self.tick_items)
        else:
            self.tickerbook[channel] = self.tickerbook[channel].append({i:msg[i] for i in self.tick_items}, ignore_index=True)

        if len(self.tickerbook[channel]['timestamp']) > self.tick_limit:
            self.tickerbook[channel] = pd.DataFrame(data=self.tickerbook[channel].values[self.tick_shave:].tolist(), columns=self.tick_items)

    # Manages your orderbook data
    async def orderbook(self, data, raw):
        channel = raw[1]
        if data['type'] == 'snapshot':
           vset = [i[1:] for i in data['bids']]
           cset = [i[1:] for i in data['asks']]
           self.bids[channel] = pd.DataFrame(data=vset, columns=['Price', 'Volume'])
           self.asks[channel] = pd.DataFrame(data=cset, columns=['Price', 'Volume'])
        elif data['type'] == 'change':
           if 'bids' in data.keys():
              for (tag, price, volume) in data['bids']:
                 BIDS = self.bids[channel]['Price'].values.tolist()
                 if tag == 'new':
                    self.bids[channel] = self.bids[channel].append({'Price': price, 'Volume': volume}, ignore_index=True)
                 if tag == 'change':
                     if price in BIDS:
                        idx = BIDS.index(price)
                        self.bids[channel]['Price'][idx] = price
                        self.bids[channel]['Volume'][idx] = volume
                     else:
                        self.bids[channel] = self.bids[channel].append({'Price': price, 'Volume': volume}, ignore_index=True)

                 if tag == 'delete':
                     if price in BIDS:
                        idx = BIDS.index(price)
                        self.bids[channel] = self.bids[channel].drop(idx)
                        #del self.bids[channel]['Price'][idx]
                        #del self.bids[channel]['Volume'][idx]

           if 'asks' in data.keys():
              for (tag, price, volume) in data['asks']:
                 ASKS = self.asks[channel]['Price'].values.tolist()
                 if tag == 'new':
                    self.asks[channel] = self.asks[channel].append({'Price': price, 'Volume': volume}, ignore_index=True)
                 if tag == 'change':
                     if price in ASKS:
                        idx = ASKS.index(price)
                        self.asks[channel]['Price'][idx] = price
                        self.asks[channel]['Volume'][idx] = volume
                     else:
                        self.asks[channel] = self.asks[channel].append({'Price': price, 'Volume': volume}, ignore_index=True)

                 if tag == 'delete':
                     if price in ASKS:
                        idx = ASKS.index(price)
                        self.asks[channel] = self.asks[channel].drop(idx)
                        #del self.asks[channel]['Price'][idx]
                        #del self.asks[channel]['Volume'][idx]
        else:
            pass

        if 'BTC-PERPETUAL' in self.bids.keys():
            if 'BTC-PERPETUAL' in self.asks.keys():
                self.booksync = True
