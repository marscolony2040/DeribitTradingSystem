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


loop = asyncio.get_event_loop()
loop.run_until_complete(websockets.serve(start, host, port))
loop.run_forever()

