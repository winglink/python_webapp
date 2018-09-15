from model import User,Blog,Comment,next_id
from webkj import get,post
import time
from aiohttp import web
import datetime
import logging;logging.basicConfig(level=logging.INFO)
from config import  configs
import hashlib
import json
from urllib import parse
from handler_by import Page

_COOKIE_NAME='wingsession'
_COOKIE_KEY='wwww'

def create_time(t):
    dt = time.time() - t
    if dt < 60:
        rs = ('%d 秒之前') % dt
    elif dt < 3600:
        rs = ('%d 分钟之前') % (dt // 60)
    elif dt < 86400:
        rs = ('%s 小时之前') % (dt // 3600)
    elif dt < 2592000:
        rs = ('%s 天之前') % (dt // (3600 * 24))
    else:
        dt = datetime.datetime.fromtimestamp(t)
        rs = ('%s年 %s月 %s日 %s时 %s分') % (dt.year, dt.month, dt.day, dt.hour, dt.minute)
    return rs
def __user2cookie(user,max_age):
         expires=str(int(time.time())+max_age)
         s='%s-%s-%s-%s' % (user.id,user.passwd,expires,_COOKIE_KEY)
         L=[user.id,expires,hashlib.sha1(s.encode('utf-8')).hexdigest()]
         return '-'.join(L)


def check_user(request):
            if hasattr(request,'__user__'):
                 return request.__user__
            else:
                 raise Exception('request has no user')

@get('/')
async def index(request):
    qs = request.query_string
    if qs:
        kw = dict()
        for k, v in parse.parse_qs(qs).items():
            kw[k] = v[0]
            page = kw.get('page_index', '1')
            page_index = int(page)
    else:
         page_index=1
    num = await Blog.find_num(args='count(id)')
    logging.info('find blog number is %s' % (num))
    p = Page(item_count=num, page_index=page_index,page_size=5)
    if num == 0:
        page=p
        blogs=()
    blogs = await Blog.findall(sorted_by='created_at')
    if (p.offset + p.limit) <= len(blogs):
        blogs = blogs[p.offset:p.offset + p.limit]
    else:
        blogs = blogs[p.offset:]
   # for blog in blogs:
    #    blog['created_at'] = create_time(blog['created_at'])


    if hasattr(request,'__user__'):
         return {
             '__template__':'blog.html',
             'blogs': blogs,
             'user':request.__user__,
             'page':p
                }
    else:
         return {
            '__template__':'blog.html',
            'blogs': blogs,
             'page':p
       }

@get('/users')
async  def get_users(request):
        users=await User.findall(sorted_by='created_at')
        return dict(users=users)

@get('/register')
async def get_register(request):
        return dict(__template__='register.html')
@get('/signout')
async def get_signout(request):
            referer=request.headers.get('Referer')
            r=web.HTTPFound(referer or '/')
            logging.info('r= %s'% (r))

            r.set_cookie(_COOKIE_NAME,'-deleted-',max_age=0,httponly=True)
            logging.info('user signed out')
            return r



@get('/signin')
async def get_signin(request):
    return dict(__template__='signin.html')
@get('/manage/blog/create')
async def get_blog_create(request):
    return dict(__template__='manage_blog_create.html',blog_id=0)
@get('/manage/blog/edit')
async def get_blogs_edit(request):
            qs=request.query_string
            if qs:
                 kw=dict()
                 for k,v in parse.parse_qs(qs).items():
                       kw[k]=v[0]
            blog_id=kw.get('blog_id')
            return dict(__template__='manage_blog_create.html',blog_id=blog_id)
@get('/manage/blogs')
async def manage_blogs(request):
    qs = request.query_string
    if qs:
        kw = dict()
        for k, v in parse.parse_qs(qs).items():
            kw[k] = v[0]
        page = kw.get('page', '1')
        page_index = int(page)
    else:
        page_index=1
    return dict(__template__='manage_blogs.html',page_index=page_index)
@get('/api/blog/delete')
async def get_api_blog_delete(request):
    logging.info('/api/blog/delete')
    qs = request.query_string
    if qs:
        kw = dict()
        for k, v in parse.parse_qs(qs).items():
            kw[k] = v[0]
    blog_id= kw.get('blog_id')
    await Blog.remove_bypk(pk=blog_id)
    r = web.Response()
    r.body = json.dumps(blog_id).encode('utf-8')
    return r
@get('/api/blog')
async def get_api_blog(request):
    qs = request.query_string
    if qs:
        kw = dict()
        for k, v in parse.parse_qs(qs).items():
            kw[k] = v[0]
    blog_id= kw.get('blog_id')
    blog=await  Blog.findall('id',blog_id)
    if  len(blog)==0:
          raise Exception('not found blog of this id ')
    blog=blog[0]
    r = web.Response()
    r.body = json.dumps(blog).encode('utf-8')
    return r

@get('/api/blogs')
async def get_api_blogs(request):
            qs=request.query_string
            if qs:
                 kw=dict()
                 for k,v in parse.parse_qs(qs).items():
                       kw[k]=v[0]
            page=kw.get('page_index','1')
            page_index=int(page)
            num=await Blog.find_num(args='count(id)')
            logging.info('find blog number is %s' % (num))
            p=Page(item_count=num,page_index=page_index)
            if num==0:
                 return dict(page=p,blogs=())
            blogs=await Blog.findall(sorted_by='created_at')
            if (p.offset+p.limit)<=len(blogs):
                 blogs=blogs[p.offset:p.offset+p.limit]
            else:
                 blogs=blogs[p.offset:]
            for blog in blogs:
                blog['created_at']=create_time(blog['created_at'])
            result=dict(page=p.__dict__,blogs=blogs)

            r = web.Response()
            r.body = json.dumps(result).encode('utf-8')

            return  r

@post('/api/blog')
async def post_api_blog(request):
    logging.info('post /api/blog')
    if request.method=='POST':
        if not request.content_type:
            return web.HTTPBadRequest('Missing Content-Type')
        ct=request.content_type.lower()
        if ct.startswith('application/json'):
            params=await request.json()
        if not isinstance(params,dict):
            return web.HTTPBadRequest('json is not dict')
        kw=params

        blog_id=kw.get('blog_id')
        name=kw.get('name')
        summary=kw.get('summary')
        content=kw.get('content')
        if not blog_id:
            raise  Exception("not find blog_id")
        if not name:
            raise  Exception("not find title")
        if not summary:
            raise  Exception("not find summary")
        if not content:
            raise  Exception("not find content")

        user=check_user(request)
        blog=Blog(id=blog_id,user_id=user.id,user_name=user.name,user_image=user.image,
                  name=name,summary=summary,content=content)
        await blog.update()
        logging.info('blog update complete')
        r = web.Response()
        r.body = json.dumps(blog).encode('utf-8')
        return r
@post('/api/blogs')
async def  api_blogs(request):
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
         summary=kw.get('summary')
         content=kw.get('content')
         if not name:
             raise  Exception("not find title")
         if not summary:
             raise  Exception("not find summary")
         if not content:
             raise  Exception("not find content")

         user=check_user(request)
         user_id=user.id
         user_name=user.name
         user_image=user.image
         blog=Blog(id=next_id(),user_id=user_id,user_name=user_name,user_image=user_image,
                   name=name,summary=summary,content=content)

         logging.info('blog save before')
         await blog.save()
         logging.info('blog save com')
         r = web.Response()
         r.body = json.dumps(blog).encode('utf-8')
         logging.info('blog wwww')
         return r

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
         password=hashlib.sha1((email+password).encode('utf-8')).hexdigest()
         user=User(id=next_id(),name=name,email=email,passwd=password,image='xxxx')
         await user.save()

         r=web.Response()

         r.set_cookie(_COOKIE_NAME,__user2cookie(user,86400),max_age=86400,httponly=True)
         r.body=json.dumps(user).encode('utf-8')
         return r


@post('/api/signin')
async def  api_signin(request):
         if request.method=='POST':
             if not request.content_type:
                    return web.HTTPBadRequest('Missing Content-Type')
             ct=request.content_type.lower()
             if ct.startswith('application/json'):
                     params=await request.json()
             if not isinstance(params,dict):
                 return web.HTTPBadRequest('json is not dict')
         kw=params

         email=kw.get('email')
         password=kw.get('password')
         if not email:
             raise  Exception("not find email")
         if not password:
             raise  Exception("not find password")
         user=await User.findall('email',email)
         if len(user)==0:
               raise Exception("not find user in sql")
         user=user[0]
         passwd_sql=user.get('passwd').strip(' ')
         if passwd_sql is None:
             raise Exception("not find passwd in sql")
         email_sql=user.get('email').strip(' ')
         if email_sql is None:
             raise Exception("not find email in sql")
         passkey=hashlib.sha1((email_sql+password).encode('utf-8')).hexdigest()
         logging.info('passkey=%s' %(passkey))
         logging.info('password=%s' %(passwd_sql))
         if passkey!=passwd_sql:
             raise Exception("password is invalid")

         # authenticate is ok ,set cookie:
         r=web.Response()
         r.set_cookie(_COOKIE_NAME,__user2cookie(user,86400),max_age=86400,httponly=True)
         user.passwd='***********'
         r.body=json.dumps(user).encode('utf-8')
         return r






