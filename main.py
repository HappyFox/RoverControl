import asyncio
import os
import pathlib

from aiohttp import web
from aiohttp.web import Application, Response, MsgType, WebSocketResponse, run_app

import botproxy
from client import Client

from pulse import pulse_task

async def wshandler(request):

    ws = web.WebSocketResponse()
    print("websocket connected");

    if not ws.can_prepare(request):
        return
    await ws.prepare(request)

    client = Client(ws, request.app['bot'])

    request.app['clients'].append(client)

    await client.handle()

    request.app['clients'].remove(client)

    return ws


async def start_background_tasks(app):
    app['pulse_task'] = app.loop.create_task(pulse_task())

async def cleanup_background_tasks(app):
    app['pulse_task'].cancel()

async def init(loop):
    app = Application(loop=loop)
    app.on_startup.append(start_background_tasks)
    app.on_cleanup.append(cleanup_background_tasks)
    app.on_shutdown.append(finish)
    app['clients'] = []
    app['bot'] = botproxy.BotProxy()
    app.router.add_route('GET', '/comms', wshandler)

    app.router.add_static('/', pathlib.Path(__file__).parent / "web_root",
                          show_index=True)

    app['handler'] = app.make_handler()
    app['srv'] = await loop.create_server(app['handler'], '127.0.0.1', 8080)

    print("Server started at http://127.0.0.1:8080")
    return app


async def finish(app):
    for client in app['clients']:
        client.close()
    app['clients'].clear()
    await asyncio.sleep(0.1)
    app['srv'].close()
    await app['handler'].finish_connections()
    await app['srv'].wait_closed()

loop = asyncio.get_event_loop()
app = loop.run_until_complete(init(loop))
run_app(app)
