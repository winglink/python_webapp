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
            user=kw.get('user'),
            password=kw.get('password'),
            db=kw.get('database'),
            charset=kw.get('charset','utf8'),
            autocommit=True,
            loop=loop
        )


async def select(sql,*args,size=None):
         #logging.info(sql,args)
         global  __pool
         with (await  __pool) as conn:
              cur=await  conn.cursor(aiomysql.DictCursor)
              await cur.execute(sql.replace('?','%s'),args)
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
                 print('sql=',sql.replace('?','%s'))
                 print('args=',args)
                 #args=tuple(args)
                # print('tuple(args)',args)
                 await  cur.execute(sql.replace('?','%s'),args)
                 print(cur.description)
                 r=await  cur.fetchall()
                 print('r=',r)
                 affected=cur.rowcount
                 print('affected',affected)
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
        attrs['__insert__']='insert into %s (`%s`,%s) values (%s)'  % (tableName,primary_key,','.join(escaped_fields),','.join(['?']*(len(escaped_fields)+1)))#vaules值为空
        attrs['__update__']='update `%s` set %s where `%s`=?' %(tableName,','.join(list(map(lambda f: '`%s`=?'  %f,fields))),primary_key)
        attrs['__delete__']='delete from %s  where `%s`=?' %(tableName,primary_key)
        return type.__new__(cls,name,bases,attrs)





class Model(dict,metaclass=ModelMetaclass):
        Start=True
        def __init__(self,**kw):
            super(Model,self).__init__(**kw)
        def __getattr__(self, key):
              try:
                   return  self[key]
              except KeyError:
                  raise AttributeError("Model object has no attribute '%s'" % key)

        def __setattr__(self, key, value):
              self[key]=value
        def getValue(self,key):
              return  self.__getattr__(key)
        def getValueordefault(self,key):
               if key not in self.keys():
                     return self.__mapping__[key].default
               else:
                   return self.__getattr__(key)


        @classmethod
        def write_sql(cls):
              if Model.Start==True:
                  Model.Start=False
                  with open('table.sql','w') as f:
                       f.write('drop database if exists webpython;\n')
                       f.write('create database webpython;\n')
                       f.write('use webpython;\n')
                       f.write('''create user 'wing'@'lcoalhost' identified by 'WING';\n''')
                       f.write('''grant select,insert, update,delete on webpython.* to 'wing'@'localhost' ;\n\n\n''')
              with open('table.sql','a') as f:
                    f.write('create table %s (\n' % cls.__name__)
                    for x,y in cls.__mapping__.items():
                         ll=[]
                         ll.append('     `%s`' % x)
                         ll.append(y.column_type)
                         ll.append('not null,\n')
                         f.write('   '.join(ll))
                    f.write('      primary key (`%s`)\n' % cls.__primary_key__)
                    f.write(') engine=innodb default charset=utf8;\n\n\n ')

        async def save(self):
                ll= [self.getValueordefault(key) for key in self.fields]
                ll.insert(0, self.getValueordefault(self.__primary_key__))
                rs=await execute(self.__insert__, ll)
                if rs!=1:
                    logging.warning('insert failed : affected rows:%s' % rs)


        async def remove(self):
               pk=self.getValueordefault(self.__primary_key__)
               r_find=await self.find(pk)
               if r_find is None:
                    logging.warning('table has no this primary_key: %s' % pk)
               rs=await  execute(self.__delete__, pk)
               if rs != 1:
                   logging.warning('delete failed : affected rows:%s' % rs)
               return  rs
        async def  update(self):
            ll = [self.getValueordefault(key) for key in self.fields]
            ll.append(self.getValueordefault(self.__primary_key__))
            r_find = await self.find(ll[-1])

            if r_find is None:
                logging.warning('table has no this primary_key: %s' % ll[-1])
            rs=await  execute(self.__update__, ll)
            if rs != 1:
                logging.warning('update  failed : affected rows:%s' % rs)
        @classmethod
        async def find_num(cls,args):
              sql='select %s from  `%s`' % (args,cls.__table__)
              rs=await  select(sql)
              num=rs[0].get(args)
              return  num

        @classmethod
        async def remove_bypk(cls, pk):
            logging.info('remove by pk = %s' % (pk))
            r_find = await cls.find(pk)
            if r_find is None:
                logging.warning('table has no this primary_key: %s' % pk)
            rs = await  execute(cls.__delete__, pk)
            if rs != 1:
                logging.warning('delete failed : affected rows:%s' % rs)
            return rs

        @classmethod
        async def find(cls, pk):  # 根据主键的值查找
            rs = await  select('%s where `%s`=? ' % (cls.__select__, cls.__primary_key__), [pk])
            if len(rs) == 0:
                return None
            return cls(**rs[0])
        @classmethod
        async def findall(cls,*args,**kw):
                sorted_by=kw.get('sorted_by')
                if len(args)>=2:
                    apd=' where  `%s`=?' %(args[0])
                    logging.info('apd=%s' %(apd))
                    rs=await select(cls.__select__+(apd),args[1])
                else:
                     rs=await  select(cls.__select__)
                if sorted_by is not None:
                     rs=sorted(rs,key=lambda u:u.get(sorted_by),reverse=True)
                return [ cls(**x) for x in rs ]


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
        def  __init__(self,name=None,primary_key=False,default=False):
                  super().__init__(name,'boolean',primary_key,default)
class FloatField(Field):
    def  __init__(self,name=None,primary_key=False,default=None):
        super().__init__(name,'real',primary_key,default)
class TextField(Field):
    def  __init__(self,name=None,primary_key=False,default=None):
        super().__init__(name,'text',primary_key,default)

