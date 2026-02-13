from typing import List

import mapper
from consts import ServiceError
from models import MessageEntity


async def get_messages(user_id: str, lover_id: str) -> List[MessageEntity]:
    session_id = f'{user_id}_{lover_id}'
    res = []
    try:
        records = await mapper.get_messages(session_id)
        if records is None or len(records) == 0:
            return res
        for record in records:
            res.append(MessageEntity(
                id=record.id,
                sender=record.type,
                content=record.content,
                timestamp=record.created_at,
                type='text'
            ))
        return res
    except ServiceError as e:
        raise e
