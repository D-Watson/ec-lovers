from models.schemas import BotPrompt
import db

session = next(db.get_bot_db())


def create_bot_prompt(bot_id: str, prompt_text: str, version: int = 1,
                      description: str = None, tags: list = None) -> BotPrompt:
    try:
        new_prompt = BotPrompt(
            bot_id=bot_id,
            prompt_text=prompt_text,
            version=version,
            description=description,
            tags=tags or []
        )
        session.add(new_prompt)
        session.commit()
        session.refresh(new_prompt)
        return new_prompt
    finally:
        session.close()


# 获取某个 bot 的当前活跃 prompt
def get_active_prompt(bot_id: str) -> BotPrompt | None:
    try:
        bot_prompt = session.query(BotPrompt).filter_by(bot_id=bot_id).first()
        return bot_prompt
    finally:
        session.close()


# 获取某个 bot 的所有版本（按 version 降序）
def get_all_versions(bot_id: str) -> list[BotPrompt]:
    try:
        return session.query(BotPrompt).filter_by(bot_id=bot_id).order_by(BotPrompt.version.desc()).all()
    finally:
        session.close()


# 根据 ID 获取
def get_prompt_by_id(prompt_id: int) -> BotPrompt | None:
    try:
        return session.get(BotPrompt, prompt_id)
    finally:
        session.close()


# 简单更新（如 description、tags）
def update_prompt(prompt_id: int, **kwargs) -> bool:
    try:
        prompt = session.get(BotPrompt, prompt_id)
        if not prompt:
            return False
        for key, value in kwargs.items():
            if hasattr(prompt, key):
                setattr(prompt, key, value)
        session.commit()
        return True
    finally:
        session.close()


# 推荐：激活一个新版本，并自动停用旧的活跃版本（原子操作）
def activate_prompt_version(prompt_id: int) -> bool:
    try:
        # 先查出该 prompt 的 bot_id
        prompt = session.get(BotPrompt, prompt_id)
        if not prompt:
            return False

        bot_id = prompt.bot_id

        # 停用该 bot 所有当前活跃的 prompt
        session.query(BotPrompt).filter(
            BotPrompt.bot_id == bot_id,
            BotPrompt.is_active == True
        ).update({"is_active": False})

        # 激活目标 prompt
        prompt.is_active = True
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def delete_prompt(prompt_id: int) -> bool:
    try:
        prompt = session.get(BotPrompt, prompt_id)
        if not prompt:
            return False
        session.delete(prompt)
        session.commit()
        return True
    finally:
        session.close()
