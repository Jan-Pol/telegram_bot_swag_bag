from db_helper import db_helper

user_state = {}
current_page = {}
user_operations = {}


def set_user_state(user_id, state):
    """Установка текущего состояния пользователя

    Args:
        user_id: Уникальный идентификатор пользователя
        state: текущее состояние пользователя. Значение из списка USER_STATES
    """
    user_state[str(user_id)] = state


def reset_user_state(user_id):
    """Сброс текущего состояния пользователя

    Args:
        user_id: Уникальный идентификатор пользователя
    """
    try:
        user_state.pop(str(user_id))
    except KeyError:
        pass


def get_user_state(user_id):
    """Получить текущее состояние пользователя

    Args:
        user_id: Уникальный идентификатор пользователя

    Returns:
        str - Текущее состояние пользователя. Значение из списка USER_STATES
        None - если информация по текущему состоянию пользователя отсутствует
    """
    return user_state.get(str(user_id), '')


def get_user_operation(user_id):
    return user_operations.get(str(user_id), None)


def add_operation(user_id, amount, operation_type, category=None):
    if not amount.isdigit():
        raise Exception(f'Переданное значение "{amount}" не является числом')
    elif float(amount) <= 0:
        raise Exception(f'Переданное значение "{amount}" меньше или равно нулю')
    else:
        user_operations[str(user_id)] = {
            'user_id': str(user_id),
            'amount': amount,
            'operation_type': operation_type,
            'category': category
        }


def increment_current_page(user_id):
    current_page_value = current_page[user_id]
    current_page[user_id] = current_page_value + 1


def decrement_current_page(user_id):
    current_page_value = current_page[user_id]
    current_page[user_id] = current_page_value - 1


def reset_current_page(user_id):
    current_page[user_id] = 0


def get_current_page(user_id):
    return current_page.get(user_id, 0)


