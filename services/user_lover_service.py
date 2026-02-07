import asyncio
import logging

import consts
import models
import mapper


def lover_add(lover: models.UserLoverCreate):
    try:
        entity = mapper.create_user_lover(lover)
        userLover = entity.toUserLover()
        return userLover
    except Exception as e:
        logging.error(f"Database integrity error: {e}")
        return None


def lover_list(user_id: str):
    res = []
    try:
        list = mapper.get_user_lovers(user_id)
        for item in list:
            res.append(item.toUserLover())
    except Exception as e:
        logging.error(f"Db query list error: {e}")
        raise consts.ServiceError(code=consts.ErrorCode.DB_ERR)
    return res


def save_prompt(lover: models.UserLover):
    prompt = consts.get_prompt(gender_id=lover.gender,
                               personality_id=lover.gender,
                               hobbies=lover.hobbies,
                               talking_style=lover.talking_style)
    try:
        botPrompt = mapper.create_bot_prompt(
            bot_id=lover.lover_id,
            prompt_text=prompt,
            version=1
        )
        logging.info(f'botPrompt info = {botPrompt}')
    except Exception as e:
        logging.error(f'[db]save prompt error={e}')
        raise consts.ServiceError(consts.ErrorCode.DB_ERR)


def delete_lover(user_id: str, lover_id: str):
    try:
        mapper.delete_user_lover(user_id, lover_id)
        mapper.delete_prompt(lover_id)

    except Exception as e:
        logging.error(f'delete lover error={e}')
        raise consts.ServiceError(consts.ErrorCode.DB_ERR)
    return False
