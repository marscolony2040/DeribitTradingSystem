import asyncio

import hmac, hashlib, base64, time, json, uuid, datetime

from manager import Database

class Sign:

    async def now(self):
        return int(time.time() * 1000)

    async def current(self):
        return int(time.time())

    async def todaysDate(self):
        n = await self.now()
        return datetime.datetime.fromtimestamp(int(n/1000)).strftime('%m-%d-%Y %H:%M:%S')

    async def nonce(self):
        return base64.b64encode(uuid.uuid1().hex.encode()).decode()

class Trader(Sign):

    # Place a buy order
    async def buy(self, ws, instrument, amount, price):
        msg = {'jsonrpc' : '2.0',
               'id' : 5275,
               'method' : 'private/buy',
               'params' : {
                        'access_token': self.auth[0],
                        'instrument_name' : instrument,
                        'amount' : amount,
                        'price': price,
                        'type' : 'limit',
                        'label' : 'quant1994'
                    }
                }
        await ws.send(json.dumps(msg))

    # Place a sell order
    async def sell(self, ws, instrument, amount, price):
        msg = {'jsonrpc' : '2.0',
               'id' : 5276,
               'method' : 'private/sell',
               'params' : {
                        'access_token': self.auth[0],
                        'instrument_name' : instrument,
                        'amount' : amount,
                        'price': price,
                        'type' : 'limit',
                        'label' : 'quant1994'
                    }
                }
        await ws.send(json.dumps(msg))

    # Allows you to edit a limit order
    async def edit(self, ws, order_id, amount, price, advanced=None):
        msg = {'jsonrpc' : '2.0',
               'id': 3725,
               'method' : 'private/edit',
               'params' : {
                    'access_token': self.auth[0],
                    'order_id': order_id,
                    'amount': amount,
                    'price': price
                    }
                }
        if advanced:
            msg['params']['advanced'] = advanced
        await ws.send(json.dumps(msg))

    # Cancel your order
    async def cancel(self, ws, order_id):
        msg = {'jsonrpc' : '2.0',
               'id': 4214,
               'method' : 'private/cancel',
               'params' : {
                    'access_token': self.auth[0],
                    'order_id': order_id,
                    }
                }
        await ws.send(json.dumps(msg)) # [result -> order -> order_id]

    # Cancel all of your orders
    async def cancel_all(self, ws):
        msg = {"jsonrpc" : "2.0",
               "id" : 8748,
               "method" : "private/cancel_all",
               "params" : {
                    "access_token": self.auth[0]
               }}
        await ws.send(json.dumps(msg))

    # Allows you to execute a block trade
    async def execute_block_trade(self, ws, currency, role, trades, cpsig):
        msg = {'jsonrpc' : '2.0',
               'id': 8731,
               'method' : 'private/execute_block_trade',
               'params' : {
                     'access_token': self.auth[0],
                     'currency' : currency,
                     'nonce' : await self.nonce(),
                     'timestamp' : await self.now(),
                     'role' : role,
                     'trades' : traders
                     },
                'counterparty_signature': cpsig
                }
        await ws.send(json.dumps(msg))

    # Verifies your block trade on the orderbook
    async def verify_block_trade(self, ws, currency, role, trades):
        msg = {'jsonrpc' : '2.0',
               'method' : 'private/verify_block_trade',
               'params' : {
                     'access_token': self.auth[0],
                     'currency' : currency,
                     'nonce' : await self.nonce(),
                     'timestamp' : await self.now(),
                     'role' : role,
                     'trades' : traders
                     }
                }
        await ws.send(json.dumps(msg))

    # Retreive your last block trades
    async def get_last_block_trades(self, ws, currency='BTC', count=1):
        msg = {'jsonrpc' : '2.0',
               'method' : 'private/get_last_block_trades_by_currency',
               'params' : {
                    'access_token': self.auth[0],
                    'currency': currency,
                    'count': count
                    }
                }
        await ws.send(json.dumps(msg))

class Account(Trader):

    # Gives you a summary of your balances
    async def get_account_summary(self, ws, currency='BTC'):
        msg = {'jsonrpc' : '2.0',
               'id' : 2515,
               'method' : 'private/get_account_summary',
               'params' : {
                   'access_token': self.auth[0],
                   'currency' : currency,
                   'extended' : True
                   }
               }
        await ws.send(json.dumps(msg))

    # Gets your position on the orderbook
    async def get_position(self, ws, instrument='BTC-PERPETUAL'):
        msg = {'jsonrpc' : '2.0',
               'id' : 404,
               'method' : 'private/get_position',
               'params' : {
                   'access_token': self.auth[0],
                   'instrument_name' : 'BTC-PERPETUAL'
                   }
               }
        await ws.send(json.dumps(msg))

    # Gets a list of multiple positions you have on the orderbook
    async def get_positions(self, ws, currency='BTC', kind='future'):
        msg = {'jsonrpc' : '2.0',
               'id' : 2236,
               'method' : 'private/get_positions',
               'params' : {
                   'access_token': self.auth[0],
                   'currency': currency,
                   'kind': kind
                   }
               }
        await ws.send(json.dumps(msg))

    # Gets your order state (whether its filled or still on the book)
    async def get_state(self, ws, order_id):
        msg = {'jsonrpc' : '2.0',
               'id' : 4316,
               'method' : 'private/get_order_state',
               'params' : {
                   'access_token': self.auth[0],
                   'order_id': order_id
                   }
              }
        await ws.send(json.dumps(msg))

    # Gets your open limit orders on the orderbook organized by currency
    async def get_open_orders_by_currency(self, ws, currency='BTC'):
        msg = {
             "jsonrpc" : "2.0",
              "id" : 1953,
              "method" : "private/get_open_orders_by_currency",
              "params" : {
                "currency" : currency
              }
        }
        await ws.send(json.dumps(msg))

class API(Account):

    def __init__(self, key, secret, channels):
        self.key = key
        self.secret = secret
        self.channels = channels
        self.url = 'wss://www.deribit.com/ws/api/v2'

        self.msgCT = 0

        self.db = Database(self)

    # Public authentication
    async def public_auth(self, ws):
        if self.msgCT == 0:
            msg = {'jsonrpc': '2.0', 'id': 9929, 'method': 'public/auth',
                   'params':{
                        'grant_type': 'client_credentials',
                        'client_id': self.key,
                        'client_secret': self.secret
                   }}
            await ws.send(json.dumps(msg))
            resp = await ws.recv()
            resp = json.loads(resp)
            if 'result' in resp.keys():
                if 'access_token' in resp['result'].keys() and 'refresh_token' in resp['result'].keys():
                    self.auth = (resp['result']['access_token'], resp['result']['refresh_token'])
                else:
                    while True: print("UNABLE TO AUTH: EXIT PROGRAM")
            else:
                while True: print("UNABLE TO AUTH: EXIT PROGRAM")

    # Private authentication
    async def private_subscribe(self, ws):
        msg = {'jsonrpc': '2.0', 'id': 4235, 'method': 'private/subscribe',
               'params':{
                    'access_token': self.auth[0],
                    'channels': self.channels
               }}
        await ws.send(json.dumps(msg))
