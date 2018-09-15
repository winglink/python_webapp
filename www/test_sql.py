import orm
from model import User,Blog,Comment
import asyncio
import json



async def test(loop):
          await  orm.create_pool(loop,user='wing',password='wing',database='webpython')
          u=User(email='bb@bb.com',name='ww',image='about:blank',id='1536851751d32e6d8c9fc14d38b48a122e9f35d05c')
          print('type of User',type(User))

          blog = Blog(id='1536852112447d160b87a24ec7aaddd532b2ca6eba', user_id= '1536851751d32e6d8c9fc14d38b48a122e9f35d05c', user_name='bbb', user_image='xxxx',
                      name='222',summary='xxx',content='xxx')
          await blog.update()
          #user=await User.find('1536671200e7d0b8f55ccb4c03be5be44f37019298')

         # print(json.dumps(dict(user=user)))

         # blog=Blog(user_id='1',user_name='sss',name='www',summary='sssss',user_image='sssss',content='sssss')
         # await blog.save()

loop=asyncio.get_event_loop()
loop.run_until_complete(test(loop))
loop.close()
