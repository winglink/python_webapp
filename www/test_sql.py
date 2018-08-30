import orm
from model import User,Blog,Comment
import asyncio



async def test(loop):
          await  orm.create_pool(loop,user='wing',password='wing',database='webpython')
          u=User(email='test@qq.com',name='ww',passwd='123',image='about:blank')
          await u.save()

       #   await u.remove()
          orm.__pool.close()
          await orm.__pool.wait_closed()

         # blog=Blog(user_id='1',user_name='sss',name='www',summary='sssss',user_image='sssss',content='sssss')
         # await blog.save()

loop=asyncio.get_event_loop()
loop.run_until_complete(test(loop))
loop.close()
