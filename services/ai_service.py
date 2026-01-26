import asyncio
import logging
from fastapi import WebSocket, WebSocketDisconnect

from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import (
    BaseChatMessageHistory,
    InMemoryChatMessageHistory,
)
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import consts
import mapper
import models

model = ChatOllama(
    model="llama3.1",
    temperature=0,
    # other params...
)
store = {}


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
    except Exception as e:
        logging.error(f'[db]save prompt error={e}')
        return


# 心跳任务
async def heartbeat(ws: WebSocket):
    while True:
        await asyncio.sleep(30)
        try:
            await ws.send({"type": "websocket.ping"})
        except:
            break


async def chat(ws: WebSocket, user_id: str, bot_id: str):
    try:
        record = mapper.get_user_lover(user_id=user_id, lover_id=bot_id)
        logging.info(f"find lover info success {record}")
    except Exception as e:
        logging.error(f"[db] query error, userId={user_id}, lover_id={bot_id}, e={e}")
        await ws.close(code=1008, reason="Invalid user pair")
        return
    await ws.accept()
    task = asyncio.create_task(heartbeat(ws))
    try:
        while True:
            try:
                # 用户发送消息
                message = await asyncio.wait_for(
                    ws.receive(),
                    timeout=65.0  # 必须 > 心跳间隔
                )
                # 请求ai
                # === 关键修改：遍历异步生成器 ===
                async for chunk in generate(bot_id=bot_id, query=message):  # 假设 message 是 dict
                    await ws.send_text(chunk)  # 流式发送每个 chunk
            except asyncio.TimeoutError:
                logging.error(f"Client timeout, closing connection")
                break
    except Exception as e:
        logging.error(f"[ws] connect error={e}")
        return
    finally:
        task.cancel()
        await ws.close()


def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]


def get_prompt(bot_id: str):
    prompt_text = mapper.get_active_prompt(bot_id)
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                prompt_text,
            ),
            MessagesPlaceholder(variable_name="messages")
        ]
    )
    return prompt


async def generate(bot_id: str, query: str):
    prompt = get_prompt(bot_id)
    chain = prompt | model
    with_message_history = RunnableWithMessageHistory(chain, get_session_history, input_messages_key="messages")
    config = {
        "configurable": {"session_id": "cookie1"}
    }
    response = with_message_history.invoke(
        {
            "messages": [HumanMessage(content=query)],
        },
        config=config,
    )
    async for chunk in with_message_history.astream(
            {"messages": [HumanMessage(content="Please give me some suggest according to my hobbies.")],
             "language": "Chinese"},
            config=config
    ):
        yield f"{chunk.content}"
