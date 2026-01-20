import logging

from sqlalchemy.orm import Session

import models
import mapper


def lover_add(db: Session, lover: models.UserLoverCreate):
    try:
        entity = mapper.create_user_lover(db, lover)
        userLover = models.UserLover(
            id=entity.id,
            lover_id=entity.lover_id,
            user_id=entity.user_id,
            avatar=entity.avatar,
            name=entity.name,
            gender=entity.gender,
            personality=entity.personality,
            hobbies=entity.hobbies,
            talking_style=entity.talking_style,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )
        return userLover
    except Exception as e:
        logging.error(f"Database integrity error: {e}")
        return None
