import logging; logging.basicConfig(level=logging.INFO)
import time
import datetime
import json
from config import configs
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
    filters=kw.get('filters')
    if filters is not None:
             env.filters=filters

    app['__template__']=env
def   create_time(t):
       dt=time.time()-t
       if dt<60:
           rs=('%d 秒之前') % dt
       elif dt<3600:
           rs=('%d 分钟之前') % (dt//60)
       elif dt<86400:
           rs=('%s 小时之前') % (dt//3600)
       elif dt<2592000:
           rs=('%s 天之前') % (dt//(3600*24))
       else:
           dt=datetime.datetime.fromtimestamp(t)
           rs=('%s年 %s月 %s日 %s时 %s分') % (dt.year,dt.month,dt.day,dt.hour,dt.minute)
       return  rs

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
                   if template_name is not None:
                       resp.pop('__template__')
                       logging.info('template_name %s' % (template_name))
                       kw=resp
                       template = app['__template__'].get_template(template_name)
                       html = template.render(**kw)
                       return web.Response(body=html, content_type='text/html', charset='utf-8')
                   else:
                       re_json=json.dumps(resp,default=lambda x:x.__dict__)
                       return web.Response(body=re_json,content_type='application/json',charset='utf-8')
               return resp
           return response
async def init(loop):
    await  orm.create_pool(loop,**configs['db'])
    app=web.Application(middlewares=[logging_m,response_factory])
    print('type(appp)=',type(app))
    print('app=',app)

    await    init_jinja2(app,auto_reload=True,filters=dict(create_time_from=create_time))    #初始化模板环境变量
    add_routes(app,'handlers')
    add_static(app)

    srv=await loop.create_server(app._make_handler(),'127.0.0.1',11000)
    logging.info('server start at http://127.0.0.1:11000')
    print('sever started at ')
    return srv

loop=asyncio.get_event_loop()
tasks=[init(loop)]
loop.run_until_complete(asyncio.wait(tasks))
loop.run_forever()

