import models
from sqlalchemy.orm import Session


# 创建
def create_user_lover(db: Session, lover: models.UserLoverCreate):
    db_lover = models.UserLoverDB(**lover.model_dump())
    db.add(db_lover)
    db.commit()
    db.refresh(db_lover)
    return db_lover


# 读取（单个）
def get_user_lover(db: Session, user_id: str, lover_id: str):
    return db.query(models.UserLoverDB).filter(
        models.UserLoverDB.user_id == user_id,
        models.UserLoverDB.lover_id == lover_id
    ).first()


# 读取（用户所有恋人）
def get_user_lovers(db: Session, user_id: str):
    return db.query(models.UserLoverDB).filter(
        models.UserLoverDB.user_id == user_id
    ).all()


# 更新
def update_user_lover(db: Session,user_id: str, lover_id: str, lover_update: models.UserLoverCreate):
    db_lover = get_user_lover(db, user_id, lover_id)
    if not db_lover:
        return None

    for key, value in lover_update.model_dump().items():
        setattr(db_lover, key, value)

    db.commit()
    db.refresh(db_lover)
    return db_lover


# 删除
def delete_user_lover(db: Session,user_id: str, lover_id: str):
    db_lover = get_user_lover(db,user_id, lover_id)
    if not db_lover:
        return False

    db.delete(db_lover)
    db.commit()
    return True