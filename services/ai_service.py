import asyncio
import logging
from fastapi import WebSocket

from langchain_core.messages import HumanMessage, AIMessage
from langchain_ollama import ChatOllama
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import consts
import mapper
import models
from mapper.chat_history_mapper import PostgresChatMessageHistoryAsync, save_messages

model = ChatOllama(
    model="llama3.1",
    temperature=0,
    # other params...
)


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
        except Exception as e:
            logging.error(f'[Heartbeat] send error={e}')
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
    # task = asyncio.create_task(heartbeat(ws))
    session_id = f'{user_id}_{bot_id}'
    try:
        while True:
            try:
                # 用户发送消息
                msg = await asyncio.wait_for(
                    ws.receive(),
                    timeout=65.0  # 必须 > 心跳间隔
                )
                print(msg)
                logging.info(f'message={msg}')
                if msg["type"] == "websocket.disconnect":
                    break
                if msg["type"] == "websocket.close":
                    logging.info("ws close.")
                    break
                user_text = msg.get("text", "")
                print(user_text)
                if not user_text.strip():
                    continue
                # === 关键修改：遍历异步生成器 ===
                async for chunk in generate_and_save(bot_id=bot_id, query=user_text, session_id=session_id):
                    await ws.send_text(chunk)  # 流式发送每个 chunk
            except asyncio.TimeoutError:
                logging.error(f"Client timeout, closing connection")
                break
    except Exception as e:
        logging.error(f"[ws] connect error={e}")
        return
    # finally:
    # task.cancel()


def get_prompt(bot_id: str):
    prompt_text = mapper.get_active_prompt(bot_id).prompt_text
    print(prompt_text)
    # todo:兜底数据
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


def get_session_history(session_id: str) -> PostgresChatMessageHistoryAsync:
    return PostgresChatMessageHistoryAsync(session_id=session_id)


async def generate_and_save(bot_id: str, query: str, session_id: str):
    prompt = get_prompt(bot_id)
    chain = prompt | model
    with_message_history = RunnableWithMessageHistory(
        chain,
        get_session_history,  # 现在返回的是异步历史对象
        input_messages_key="messages"
    )
    config = {"configurable": {"session_id": session_id}}
    full_response = ""
    async for chunk in with_message_history.astream(
            {"messages": [HumanMessage(content=query)]},
            config=config
    ):
        content = chunk.content if hasattr(chunk, 'content') else str(chunk)
        full_response += content
        yield content
    logging.info(f'full response={full_response}')
    # 保存历史记录
    await save_messages(
        session_id=session_id,
        messages=[HumanMessage(content=query), AIMessage(content=full_response)]
    )
