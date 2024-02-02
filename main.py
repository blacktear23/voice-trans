#!/usr/bin/env python3
import sys
import time
import wsock
import server
import argparse
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


def help():
    print('''python3 main.py [command] [options]

commands:
    glmapi  start chatGLM API server
    web     start Web Server
''')
    exit(1)


def run_web_api_server(args):
    parser = argparse.ArgumentParser(prog='web', description='run web server')
    parser.add_argument('-l', dest='host', default='127.0.0.1', help='listen address')
    parser.add_argument('-p', dest='port', type=int, default=7880, help='listen port')
    parser.add_argument('-d', dest='debug', action='store_true', default=False, help='enable debug mode')
    args = parser.parse_args(args)
    host = args.host
    port = args.port
    debug = args.debug
    wst = WSThread(host, port + 1)
    wst.start()
    server.start_server(host, port, debug)
    wst.kill()


def run_glm_api_server(args):
    from services.chatglm_srv import run_chatglm_api
    parser = argparse.ArgumentParser(prog='web', description='run web server')
    parser.add_argument('-l', dest='host', default='127.0.0.1', help='listen address')
    parser.add_argument('-p', dest='port', type=int, default=8889, help='listen port')
    parser.add_argument('-d', dest='debug', action='store_true', default=False, help='enable debug mode')
    args = parser.parse_args(args)
    host = args.host
    port = args.port
    debug = args.debug
    run_chatglm_api(host, port, debug)


if __name__ == '__main__':
    args = sys.argv
    if len(args) < 2:
        help()

    cmd = args[1]
    if cmd == 'glmapi':
        run_glm_api_server(args[2:])
    elif cmd == 'web':
        run_web_api_server(args[2:])
    else:
        help()
