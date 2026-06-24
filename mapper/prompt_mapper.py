# SECURITY-REVIEWED: 2026-06-24 | RULES: v2.6.0-draft
import logging

from models.schemas import BotPrompt
from db.postgre_engine import BizSessionLocal


def create_bot_prompt(bot_id: str, prompt_text: str, version: int = 1,
                      description: str = None, tags: list = None) -> BotPrompt:
    with BizSessionLocal() as session:
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


def get_active_prompt(bot_id: str) -> BotPrompt | None:
    with BizSessionLocal() as session:
        return session.query(BotPrompt).filter_by(bot_id=bot_id).first()


def get_all_versions(bot_id: str) -> list[BotPrompt]:
    with BizSessionLocal() as session:
        return session.query(BotPrompt).filter_by(bot_id=bot_id).order_by(BotPrompt.version.desc()).all()


def get_prompt_by_id(prompt_id: int) -> BotPrompt | None:
    with BizSessionLocal() as session:
        return session.get(BotPrompt, prompt_id)


def update_prompt(prompt_id: int, **kwargs) -> bool:
    with BizSessionLocal() as session:
        prompt = session.get(BotPrompt, prompt_id)
        if not prompt:
            return False
        for key, value in kwargs.items():
            if hasattr(prompt, key):
                setattr(prompt, key, value)
        session.commit()
        return True


def activate_prompt_version(prompt_id: int) -> bool:
    with BizSessionLocal() as session:
        try:
            prompt = session.get(BotPrompt, prompt_id)
            if not prompt:
                return False

            bot_id = prompt.bot_id

            session.query(BotPrompt).filter(
                BotPrompt.bot_id == bot_id,
                BotPrompt.is_active == True
            ).update({"is_active": False})

            prompt.is_active = True
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e


def delete_prompt(bot_id: str) -> bool:
    with BizSessionLocal() as session:
        count = session.query(BotPrompt).filter(
            BotPrompt.bot_id == bot_id
        ).delete()
        logging.info(f"Deleted {count} prompts for bot_id={bot_id}")
        session.commit()
        return True
