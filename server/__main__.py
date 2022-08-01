import asyncio
import websockets
import threading
import json
import time
from subprocess import call

from home import System


host = 'localhost'
port = 5678

# Starts system
async def start(ws, path):
    key = ''
    secret = ''
    channels = ['book.BTC-PERPETUAL.100ms',
                'ticker.BTC-PERPETUAL.raw']
    await System(key, secret, channels).start(ws)

# Decorator handles system error and reboots
def refresher(f):
    def handle(*a, **b):
        while True:
            try:
                print('RAZR Trading System')
                f(*a, **b)
            except Exception as e:
                print('System Error, Rebooting: {}'.format(e))
            time.sleep(3)
    return handle

# Decorator creates thread
def multi(f):
    def threader(*a, **b):
        return threading.Thread(target=lambda: f(*a, **b))
    return threader

# Opens server connection
@multi
def server():
    print('Starting Python Server')
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(websockets.serve(start, host, port))
    loop.run_forever()

# Opens React.js client
@multi
def client():
    print('Starting React FrontEnd')
    time.sleep(2.67)
    call(["npm", "start"])

# Main function opens and starts the client/server threads
@refresher
def main(s, c):
    for y in (s, c): y.start()
    for y in (s, c): y.join()

# Trading system opener
main(server(), client())
