import functools
import logging;logging.basicConfig(level=logging.INFO)
import asyncio
import os
from inspect import isfunction
def get(path):

        def decorator(func):
             @functools.wraps(func)
             def wrapper(*args,**kw):
                  return func(*args,**kw)
             wrapper.__method__='GET'
             wrapper.__route__=path
             return wrapper
        return  decorator

def post(path):

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args,**kw):
            return func(*args,**kw)
        wrapper.__method__='POST'
        wrapper.__route__=path
        return wrapper
    return  decorator

class RequestHandler(object):

          def __init__(self,app,fn):
                 self._app=app
                 self._func=fn

          async def __call__(self,request):
                 pass
                 r=await  self._func(**kw)
                 return r
def  add_static(app):
        path=os.path.join(os.path.abspath('.'),'static')
        app.router.add_static('/static/',path)
        logging.info('add static path: %s' % path)



def  add_route(app,fn):
       method=getattr(fn,'__method__',None)
       path=getattr(fn,'__route__',None)
       if path is None or method is None:
             raise ValueError('@get or @post no defined in %s.' % str(fn))
       if not asyncio.iscoroutinefunction(fn):
              fn=asyncio.coroutine(fn)
       logging.info('add route %s %s => %s ' % (method,path,fn.__name__))
       app.router.add_route(method,path,fn)

def add_routes(app,module_name):
        mod=__import__(module_name,globals(),locals())
        logging.info('add_routes')
        for  fn in  dir(mod):
              if  fn.startswith('__') or fn=='get' or fn=='post' or fn.startswith('next'):
                  pass
              else:
                   fn=getattr(mod,fn)
                   if isfunction(fn):
                       add_route(app,fn)
                       logging.info('add_route fn=%s' %fn)


