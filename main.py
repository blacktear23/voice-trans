#!/usr/bin/env python3
import time
import server
import wsock
from threading import Thread


class WSThread(Thread):
    def __init__(self, host, port):
        super(WSThread, self).__init__()
        self.host = host
        self.port = port
        self.loop = None

    def run(self):
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self.loop = loop
        wsock.run_server(self.host, self.port)

    async def stop_loop(self):
        self.loop.stop()

    def kill(self):
        if self.loop is not None:
            self.loop.call_soon_threadsafe(self.loop.stop)


if __name__ == '__main__':
    host = '127.0.0.1'
    port = 7880
    wst = WSThread(host, port + 1)
    wst.start()
    server.start_server(host, port, True)
    wst.kill()
