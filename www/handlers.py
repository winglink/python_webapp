from model import User,Blog,Comment
from webkj import get,post
@get('/')
async def index(request):
     users=await User.findall()
     return {
            '__template__':'test.html',
            'users': users
     }



