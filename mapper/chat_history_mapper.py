import logging
from typing import List, Sequence

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from sqlalchemy import select

import db
from models.schemas.message_store import MessageStore  # 你的 ORM 模型


class PostgresChatMessageHistoryAsync(BaseChatMessageHistory):

    def __init__(self, session_id: str):
        self.session_id = session_id

    async def aget_messages(self) -> List[BaseMessage]:
        AsyncSessionLocal = db.get_msg_session()
        """异步获取消息"""
        try:
            async with AsyncSessionLocal() as session:
                records = await session.execute(
                    select(MessageStore).
                    where(MessageStore.session_id == self.session_id).
                    order_by(MessageStore.created_at)
                )
                print(records)
                if records is None:
                    return []
                messages = []
                for row in records.scalars():
                    msg_class = HumanMessage if row.type == "human" else AIMessage
                    messages.append(msg_class(content=row.content))
                return messages
        except Exception as e:
            logging.error(f"[db] query message history error={e}")
            return []

    async def aadd_messages(self, messages: Sequence[BaseMessage]) -> None:
        pass

    async def clear(self) -> None:
        pass

    async def aclear(self) -> None:  # ✅ 严格匹配签名
        pass


async def save_messages(session_id: str, messages: Sequence[BaseMessage]) -> None:
    """异步添加消息"""
    AsyncSessionLocal = db.get_msg_session()
    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():  # 开启事务
                for msg in messages:
                    msg_type = "human" if isinstance(msg, HumanMessage) else "ai"
                    newMsg = MessageStore(
                        session_id=session_id,
                        type=msg_type,
                        content=msg.content
                    )
                    session.add(newMsg)
    except Exception as e:
        logging.error(f'error={e}')
        return
