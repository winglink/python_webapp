import logging;logging.basicConfig(level=logging.INFO)
import asyncio
import aiomysql



async def create_pool(loop,**kw):
        logging.info('create database connection pool')
        global __pool
        __pool=await  aiomysql.create_pool(
            minsize=kw.get('minsize',1),
            maxsize=kw.get('maxsize',10),
            host=kw.get('host','localhost'),
            port=kw.get('port',3306),
            user=kw.get('root'),
            password=kw.get('password'),
            db=kw.get('database'),
            charset=kw.get('charset','utf8'),
            loop=loop
        )


async def select(sql,args,size=None):
         #logging.info(sql,args)
         global  __pool
         with (await  __pool) as conn:
              cur=await  conn.cursor(aiomysql.DictCursor)
              await cur.execute(sql.replace('?','%s'),args or())
              if size:
                  rs=await cur.fetchmany(size)
              else:
                  rs=await cur.fetchall()
                  logging.info('rows returned:%s' % len(rs))
                  await  cur.close()
                  return rs

async def execute(sql,args):
        # logging.info(sql,args)
        global __pool
        with (await __pool) as conn:
            try:

                 cur=await conn.cursor()
                 await  cur.execute(sql.replace('?','%s'),args)
                 affected=cur.rowcount
                 await cur.close()
            except BaseException as e:
                 raise
            return affected


class ModelMetaclass(type):
    def __new__(cls, name, bases, attrs):
        print(cls,name,bases,attrs)
        if name == 'Model':
            return  type.__new__(cls,name,bases,attrs)
        tableName=attrs.get('__table__',None) or name
        logging.info('found Model: %s(talbe:%s)' %(name,tableName))

        mapping=dict()
        fields=[]
        primary_key=None
        for k,v in attrs.items():
            print(k,v)
            if isinstance(v,Field):
                 mapping[k]=v
                 if v.primary_key:
                     if primary_key:
                        raise RuntimeError('Duplicate primary key for field： %s'  %(k))
                     primary_key=k
                 else:
                    fields.append(k)
        if not primary_key:
             raise RuntimeError('Primary key not found')
        for k in mapping.keys():
             attrs.pop(k)
        escaped_fields=list(map(lambda f:'`%s`' %f,fields))
        attrs['__mapping__']=mapping
        attrs['__table__']=tableName
        attrs['__primary_key__']=primary_key
        attrs['fields']=fields
        attrs['__select__']='select `%s`,%s from `%s`' % (primary_key,','.join(escaped_fields),tableName)
        attrs['__insert__']='insert into `%s` (`%s`,%s) values (%s)'  % (tableName,primary_key,','.join(escaped_fields),','.join(['?']*(len(escaped_fields)+1)))#vaules值为空
        attrs['__update__']='update `%s` set %s where `%s`=?' %(tableName,','.join(list(map(lambda f: '`%s`=?'  %f,fields))),primary_key)
        attrs['__delete__']='delete from `%s` where `%s`=?' %(tableName,primary_key)
        return type.__new__(cls,name,bases,attrs)





class Model(dict,metaclass=ModelMetaclass):
        Start=True
        def __init__(self,**kw):
            super(Model,self).__init__(**kw)
            print('Model000000000000000000000')
        def __getattr__(self, key):
              try:
                   return  self[key]
              except KeyError:
                  raise AttributeError("Model object has no attribute '%s'" % key)

        def __setattr__(self, key, value):
              self[key]=value
        def getValue(self,key):
              return  self.__getattr__(key)

        @classmethod
        async def find(cls,pk):    #根据主键的值查找
             rs=await  select('%s where `%s`=? ' % (cls.__select__,cls.__primary_key__),[pk])
             if len(rs)==0:
                 return None
             return cls(**rs[0])
        @classmethod
        def write_sql(cls):
              if Model.Start==True:
                  Model.Start=False
                  with open('table.sql','w') as f:
                       f.write('drop database if exists webpython;\n')
                       f.write('create database webpython;\n')
                       f.write('use webpython;\n')
                       f.write('''grant select,insert, update,delete on webpython.* to 'www-data'@'localhost' identified by 'www-data';\n\n\n''')
              with open('table.sql','a') as f:
                    f.write('create table %s (\n' % cls.__name__)
                    for x,y in cls.__mapping__.items():
                         ll=[]
                         ll.append('     `%s`' % x)
                         ll.append(y.column_type)
                         ll.append('not null,\n')
                         f.write('   '.join(ll))
                    f.write('      primary key (`%s`),\n' % cls.__primary_key__)
                    f.write(') engine=innodb default charset=utf8;\n\n\n ')

        async def save(self):
                ll= [self.getValue(key) for key in self.__fields__]
                ll.insert(0, self.getValue(self.__primary_key__))

                rs=await execute(self.__insert__, ll)
                if rs!=1:
                    logging.warning('insert failed : affected rows:%s' % rs)

        async def remove(self):
               pk=self.getValue(self.__primary_key__)
               r_find=self.find(pk)
               if r_find is None:
                    logging.warning('table has no this primary_key: %s' % pk)
               rs=await  execute(self.__delete__, pk)
               if rs != 1:
                   logging.warning('delete failed : affected rows:%s' % rs)

        async def  update(self):
            ll = [self.getValue(key) for key in self.__fields__]
            ll.append(self.getValue(self.__primary_key__))
            r_find = self.find(ll[-1])
            if r_find is None:
                logging.warning('table has no this primary_key: %s' % ll[-1])
            rs=await  execute(self.__update__, ll)
            if rs != 1:
                logging.warning('update  failed : affected rows:%s' % rs)

class Field(object):
       def __init__(self,name,column_type,primary_key,default):
            self.name=name
            self.column_type=column_type
            self.primary_key=primary_key
            self.default=default
       def __str__(self):
            return '<%s,%s,%s' % (self.__class__.__name__,self.column_type,self.name)

class StringField(Field):
        def __init__(self,name=None,primary_key=False,default=None,ddl='varchar(100)'):
               super().__init__(name,ddl,primary_key,default)

class IntegerField(Field):
        def __init__(self,name=None,primary_key=False,default=None):
                super().__init__(name,'bigint',primary_key,default)

class BooleanField(Field):
        def  __init__(self,name=None,primary_key=False,default=None):
                  super().__init__(name,'boolean',primary_key,default)
class FloatField(Field):
    def  __init__(self,name=None,primary_key=False,default=None):
        super().__init__(name,'real',primary_key,default)
class TextField(Field):
    def  __init__(self,name=None,primary_key=False,default=None):
        super().__init__(name,'text',primary_key,default)

