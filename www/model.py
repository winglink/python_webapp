from orm import  Model,StringField,BooleanField,TextField,FloatField
import time,uuid

def next_id():
        return  '%d%s' %(time.time(),uuid.uuid4().hex)


class User(Model):
        __table__='user'

        id=StringField(primary_key=True,ddl='varchar(50)',default=next_id())
        email=StringField(ddl='varchar(50)')
        passwd=StringField(ddl='varchar(50)')
        admin=BooleanField()
        name=StringField(ddl='varchar(50)')
        image=StringField(ddl='varchar(500)')
        created_at=FloatField(default=time.time())
class Blog(Model):
        __table__='blog'

        id=StringField(primary_key=True,ddl='varchar(50)',default=next_id())
        user_id=StringField(ddl='varchar(50)')
        user_name=StringField(ddl='varchar(50)')
        user_image=StringField(ddl='varchar(500)')
        name=StringField(ddl='varchar(50)')
        summary=StringField(ddl='varchar(50)')
        content=TextField()
        created_at=FloatField(default=time.time())

class Comment(Model):
        __table__='comment'

        id=StringField(primary_key=True,ddl='varchar(50)',default=next_id())
        blog_id=StringField(ddl='varchar(50)')
        user_id=StringField(ddl='varchar(50)')
        user_name=StringField(ddl='varchar(50)')
        user_image=StringField(ddl='varchar(500)')
        content=TextField()
        created_at=FloatField(default=time.time())

