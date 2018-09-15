import logging; logging.basicConfig(level=logging.INFO)
import time
import datetime
import json
from config import configs
from aiohttp import  web
from jinja2 import   PackageLoader,Environment,FileSystemLoader
import orm
import hashlib
from model import User,Blog,Comment
import os
import asyncio
from webkj import *
_COOKIE_NAME='wingsession'
_COOKIE_KEY='wwww'
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
async def get_user(cookie):
               cookie_l=cookie.split('-')
               if len(cookie_l)!=3:
                    logging.info('wrong cookie')
                    return None
               t_now=time.time()
               if t_now>float(cookie_l[1]):
                      logging.info('out of expire time')
                      return  None
               user=await User.find(cookie_l[0])
               if  user is None:
                      logging.info("don't have this user")
                      return None
               s = '%s-%s-%s-%s' % (user.id, user.passwd, cookie_l[1], _COOKIE_KEY)
               hash=hashlib.sha1(s.encode('utf-8')).hexdigest()
               if hash==cookie_l[2]:
                   logging.info('set current user: %s' %(user.email))
                   return user


@web.middleware
async def auth_factory(request,handler):
    logging.info("Checkuser: %s %s" % (request.method,request.path))
    cookie=request.cookies.get(_COOKIE_NAME)
    has_user=None
    if  cookie:
          user=await get_user(cookie)
          if user is not None:
              request.__user__=user
              has_user=True
          else:
              has_user=False
    if request.path.startswith('/manage') and hasattr(request,'__user__')==False:
           logging.info('111')
           return  web.HTTPFound('/signin')
    if request.path.startswith('/manage') and hasattr(request,'__user__')==True and request.__user__.admin==False:
          logging.info('2222')
          logging.info('admin %s' %(request.__user__.admin))
          return  web.HTTPFound('/signin')
    response=await  handler(request)
    return response


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
    app=web.Application(middlewares=[logging_m,response_factory,auth_factory])
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

