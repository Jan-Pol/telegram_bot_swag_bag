record_dict = {}


def record_to_dict(chat_id, k, v):
    if chat_id in record_dict:
        record_dict.get(chat_id).update({k: v})
    else:
        record_dict.update({chat_id: {k: v}})
