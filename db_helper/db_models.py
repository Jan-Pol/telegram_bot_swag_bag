from playhouse.migrate import *
import csv
import callback_data
import datetime
from playhouse.dataset import DataSet


db = SqliteDatabase('app.db', pragmas={'foreign_keys': 1})


class BaseModel(Model):
    class Meta:
        database = db


class Users(BaseModel):
    user_id = IntegerField(primary_key=True)
    user_name = CharField()
    first_name = CharField()
    last_name = CharField(null=True)
    join_date = DateTimeField()


class CertifiedUsers(BaseModel):
    id = IntegerField(primary_key=True)
    number_phone = CharField()
    fio = CharField()


class KindOfActivity(BaseModel):
    koa_id = AutoField()
    koa_name = CharField()


class TypeTask(BaseModel):
    tt_id = AutoField()
    tt_name = CharField()


class AS(BaseModel):
    as_id = AutoField()
    as_name = CharField()


class RecordsWorkTime(BaseModel):
    user_id = ForeignKeyField(model=Users)
    koa_id = ForeignKeyField(model=KindOfActivity)
    as_id = ForeignKeyField(model=AS)
    tt_id = ForeignKeyField(model=TypeTask)


if __name__ == "__main__":
    db.connect()
    # db.create_tables([Users, KindOfActivity, AS, RecordsWorkTime, TypeTask])
    db.create_tables([TypeTask])
    a = TypeTask.create(tt_name='Простая задача')
    b = TypeTask.create(tt_name='Сложная задача')
    '''    
    koa = KindOfActivity.create(koa_id='0', koa_name='Работал')
    ko = KindOfActivity.create(koa_id='1', koa_name='Хуярил')
    ka = KindOfActivity.create(koa_id='2', koa_name='Ебашил')
    k = KindOfActivity.create(koa_id='3', koa_name='ЗАРАБАТЫВАЛ')
    user = Users.create(user_name='test', first_name='test', last_name='test', join_date="2013-08-23 10:18:32.926")
    v = AS.create(as_name='ДРУГ')
    x = AS.create(as_name='МЕГА ЦУКС')
    
    sys_user = Users(user_name='test', first_name='test', last_name='test', join_date="2013-08-23 10:18:32.926")
    sys_user.save()
    
    db.create_tables([KindOfActivity])
    koa = KindOfActivity.create(koa_id='3', koa_name='Четвертушка')    
    sys_user = Users(user_name='test', first_name='test', last_name='test', join_date="2013-08-23 10:18:32.926")
    sys_user.save()
    
    a = Users.select().where(Users.user_id == 1).get()
    # a = Users.select().where(Users.user_name == 'test').get()
    print(a.last_name)
    db.close()

    db.create_tables([Person])
    uncle_bob = Person(name='Bob', birthday=date(1960, 1, 15), is_relative=True)
    uncle_bob.save()
    a = Person.select().where(Person.name == 'Bob').get()
    print(a.birthday)
'''
    # migrator = SqliteMigrator(db)
    # migrate(
    #     migrator.add_column('card', 'difficulty', Card.difficulty),
    # )

