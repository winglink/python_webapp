from aiohttp import  web
import asyncio


async def index(request):
     return web.Response(body='wing',content_type='text/html')

async def init(loop):
    app=web.Application()
    app.router.add_get('/',index)
    srv=await loop.create_server(app._make_handler(),'127.0.0.1',8000)
    print('sever started at ')
    return srv

loop=asyncio.get_event_loop()
loop.run_until_complete(init( loop))
loop.run_forever()

