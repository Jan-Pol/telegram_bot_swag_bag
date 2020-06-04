import logging
from datetime import datetime
import uuid

import user_state
from db_helper.db_models import *

logger = logging.getLogger('peewee')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


def check_user_existence(chat_id):
    """Проверка существования пользователя с заданным chat_id

    Args:
        chat_id: уникальный идентификатор пользователя

    Returns: True - пользователь существует
             False - пользователь не существует
    """

    try:
        Users.get(Users.user_id == chat_id)
        return True
    except DoesNotExist:
        return False


def create_user(message):
    user_id = message.chat.id
    user_name = message.chat.username
    first_name = message.chat.first_name
    last_name = message.chat.last_name
    join_date = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M:%S.%f")

    user = Users.create(user_id=user_id,
                        user_name=user_name,
                        first_name=first_name,
                        last_name=last_name,
                        join_date=join_date)
    return user


def get_kind_of_activity():
    koa_list = KindOfActivity.select(KindOfActivity.koa_id, KindOfActivity.koa_name)
    output = [e[1] for e in koa_list.tuples()]
    for i in range(len(output)):
        callback_data.CALLBACK_DATA.update({output[i]: 'koa' + str(i)})
    return output


def get_as():
    as_list = AS.select(AS.as_id, AS.as_name)
    output = [e[1] for e in as_list.tuples()]
    for i in range(len(output)):
        callback_data.CALLBACK_DATA.update({output[i]: 'as' + str(i)})
    return output


def get_type_task():
    type_task_list = TypeTask.select(TypeTask.tt_id, TypeTask.tt_name)
    output = [e[1] for e in type_task_list.tuples()]
    for i in range(len(output)):
        callback_data.CALLBACK_DATA.update({output[i]: ' type_task' + str(i)})
    return output


def get_certified_users_dict(chat_id, number_phone):
    certified_users_dict = {}
    try:
        output = CertifiedUsers.get(CertifiedUsers.number_phone == number_phone)
    except DoesNotExist:
        return 0
    try:
        query = CertifiedUsers.update(id=chat_id).where(CertifiedUsers.number_phone == number_phone)
        n = query.execute()
    except IntegrityError:
        query = CertifiedUsers.update(id=id).where(CertifiedUsers.id == chat_id)
        n = query.execute()
        query = CertifiedUsers.update(id=chat_id).where(CertifiedUsers.number_phone == number_phone)
        n = query.execute()
    print('# of rows updated: {}'.format(n))
    # CertifiedUsers.update(id=chat_id).where(CertifiedUsers.number_phone == number_phone)
    # output = CertifiedUsers.get(CertifiedUsers.number_phone == number_phone)
    # print(output.id)
    certified_users_dict.update({'id': chat_id,
                                 'number_phone': output.number_phone,
                                 'fio': output.fio
                                 })
    return certified_users_dict


def add_operation(user_id, operation):
    operation_date = datetime.strftime(datetime.now(), "%Y-%m-%d")
    new_operation = Operations.create(amount=operation['amount'],
                                      operation_date=operation_date,
                                      user_id=user_id,
                                      category=operation['category'],
                                      operation_type_id=operation['operation_type'])
    return new_operation


def change_operation_comment(operation_id, new_comment):
    Operations.update(operation_comment=new_comment).where(Operations.operation_id == operation_id).execute()


def get_operation_by_id(operation_id):
    return Operations.get(Operations.operation_id == operation_id)


def add_category(user_id, category_name, operation_type):
    new_category = Categories.create(category_name=category_name,
                                     user_id=user_id,
                                     operation_type_id=operation_type)
    return new_category
