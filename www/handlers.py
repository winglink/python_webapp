from model import User,Blog,Comment,next_id
from webkj import get,post
import time
from aiohttp import web
import logging;logging.basicConfig(level=logging.INFO)
from config import  configs
import hashlib
import json


_COOKIE_NAME='wingsession'
_COOKIE_KEY='wwww'
def __user2cookie(user,max_age):
         expires=str(int(time.time())+max_age)
         s='%s-%s-%s-%s' % (user.id,user.passwd,expires,_COOKIE_KEY)
         L=[user.id,expires,hashlib.sha1(s.encode('utf-8')).hexdigest()]
         return '-'.join(L)


@get('/')
async def index(request):
     summary="dfs fds sfgsgfgafdsf"
     blogs=[
            Blog(user_name='aa',summary=summary,name='learn py',created_at=time.time()-10000),
            Blog(user_name='bb',summary=summary,name='learn aa',created_at=time.time()-2000),
            Blog(user_name='cc',summary=summary,name='learn cc',created_at=time.time()-999)
     ]
     return {
            '__template__':'blog.html',
            'blogs': blogs
     }

@get('/users')
async  def get_users(request):
        users=await User.findall(sorted_by='created_at')
        return dict(users=users)

@get('/register')
async def get_register(request):
        return dict(__template__='register.html')

@post('/api/users')
async def  api_register_user(request):
         if request.method=='POST':
             if not request.content_type:
                    return web.HTTPBadRequest('Missing Content-Type')
             ct=request.content_type.lower()
             if ct.startswith('application/json'):
                     params=await request.json()
             if not isinstance(params,dict):
                 return web.HTTPBadRequest('json is not dict')
         kw=params

         name=kw.get('name')
         email=kw.get('email')
         password=kw.get('password')
         if not name:
              raise  Exception("not find name")
         if not email:
             raise  Exception("not find email")
         if not password:
             raise  Exception("not find password")
         users=await User.findall('email',email)
         if len(users)>0 :
              raise Exception("email is already in use")
         user=User(id=next_id(),name=name,email=email,passwd=password,image='xxxx')
         await user.save()

         r=web.Response()

         r.set_cookie(_COOKIE_NAME,__user2cookie(user,86400),max_age=86400,httponly=True)
         r.body=json.dumps(user).encode('utf-8')
         return r









