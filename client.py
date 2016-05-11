import json

from aiohttp import web


class Client(object):

    def __init__(self, ws, bot_proxy):
        self.ws = ws
        self.bot = bot_proxy

        self.update()

    def update(self):
        msg = StateMsg(cmd_count=self.bot.cmd_count())
        self.ws.send_str(msg.to_json())

    def close(self):
        print("We be closing!")
        self.ws.close()

    async def handle(self):
        async for msg in self.ws:
            if msg.tp == web.MsgType.text:
                self.ws.send_str("Hello, {}".format(msg.data))
            elif msg.tp == web.MsgType.binary:
                self.ws.send_bytes(msg.data)
            elif msg.tp == web.MsgType.close:
                print("We be closing!")
                break


class StateMsg(object):

    type = "state"
    def __init__(self, connected=False, cmd_count=0):
        self.connected = connected
        self.cmd_count = cmd_count

    def to_json(self):
        return json.dumps({"type": self.type, "payload":
                                                {"cmd_count": self.cmd_count}})
