import os
import asyncio
from aiohttp import web
from aiohttp.web import Application, Response, MsgType, WebSocketResponse

import botproxy
from client import Client

async def wshandler(request):

    ws = web.WebSocketResponse()

    if not ws.can_prepare(request):
        return
    await ws.prepare(request)

    client = Client(ws, request.app['bot'])

    request.app['clients'].append(client)

    await client.handle()

    request.app['clients'].remove(client)

    return ws

def view_factory(url, path):
    async def static_view(request):
        prefix = url.rsplit('/', 1)[0] or '/'
        route = web.StaticRoute(None, prefix, os.path.dirname(__file__))

        request.match_info['filename'] = path
        return await route.handle(request)
    return static_view


async def init(loop):
    app = Application(loop=loop)
    app['clients'] = []
    app['bot'] = botproxy.BotProxy()
    app.router.add_route('GET', '/comms', wshandler)

    app.router.add_route('GET', '/', view_factory('/', 'pages/index.html'))
    app.router.add_route('GET',
                         '/favicon.ico',
                         view_factory('/favicon.ico', 'favicon/favicon.ico'))

    app.router.add_static('/pages/', os.path.join(os.getcwd(), 'pages'), name='pages')
    app.router.add_static('/js/', os.path.join(os.getcwd(), 'js'), name='js')

    handler = app.make_handler()
    srv = await loop.create_server(handler, '127.0.0.1', 8080)
    print("Server started at http://127.0.0.1:8080")
    return app, srv, handler


async def finish(app, srv, handler):
    for client in app['clients']:
        client.close()
    app['clients'].clear()
    await asyncio.sleep(0.1)
    srv.close()
    await handler.finish_connections()
    await srv.wait_closed()

loop = asyncio.get_event_loop()
app, srv, handler = loop.run_until_complete(init(loop))
try:
    loop.run_forever()
except KeyboardInterrupt:
    loop.run_until_complete(finish(app, srv, handler))
