import logging; logging.basicConfig(level=logging.INFO)
from aiohttp import  web
from jinja2 import   PackageLoader,Environment,FileSystemLoader
import orm
from model import User,Blog,Comment
import os
import asyncio
from webkj import *

async def init_jinja2(app,**kw):
    option=dict(
            auto_reload=kw.get('auto_reload',True)
    )
    path=os.path.join(os.path.abspath('.'),'templates')
    env = Environment(loader=FileSystemLoader(path),**option)
    app['__template__']=env
@web.middleware
async def logging_m(request,handler):
        logging.info("Request: %s %s" % (request.method,request.path))
        response= await handler(request)
        return response
async def response_factory(app,handler):
           async def response(request):
               resp = await handler(request)
               if type(resp) is dict:
                   template_name = resp.get('__template__', None)
                   resp.pop('__template__')
                   kw=resp
                   if template_name is not None:
                       template = app['__template__'].get_template(template_name)
                       html = template.render(**kw)
               return web.Response(body=html, content_type='text/html', charset='utf-8')
           return response
async def init(loop):
    await  orm.create_pool(loop, user='wing', password='wing', database='webpython')
    app=web.Application(middlewares=[logging_m,response_factory])
    print('type(appp)=',type(app))
    print('app=',app)

    await    init_jinja2(app,auto_reload=True)    #初始化模板环境变量
    add_routes(app,'handlers')

    srv=await loop.create_server(app._make_handler(),'127.0.0.1',8000)
    logging.info('server start at http://127.0.0.1:8000')
    print('sever started at ')
    return srv

loop=asyncio.get_event_loop()
tasks=[init(loop)]
loop.run_until_complete(asyncio.wait(tasks))
loop.run_forever()

