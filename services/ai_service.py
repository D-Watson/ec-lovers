import asyncio
import logging
import os

from fastapi import WebSocket

from langchain_core.messages import HumanMessage, AIMessage
from langchain_ollama import ChatOllama
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import consts
import mapper
import models
from services.cos_services import CosService
from services.image_generate import ImageGenerate
from mapper.chat_history_mapper import PostgresChatMessageHistoryAsync, save_messages


class AIServer(object):
    def __init__(self, user_id: str, lover_id: str):
        self.model = ChatOllama(
            model="llama3.1",
            temperature=0,
            # other params...
        )
        self.user_id = user_id
        self.lover_id = lover_id

    # 心跳任务
    async def heartbeat(self, ws: WebSocket):
        while True:
            await asyncio.sleep(30)
            try:
                await ws.send({"type": "websocket.ping"})
            except Exception as e:
                logging.error(f'[Heartbeat] send error={e}')
                break

    async def chat(self, ws: WebSocket):
        try:
            record = mapper.get_user_lover(user_id=self.user_id, lover_id=self.lover_id)
            logging.info(f"find lover info success {record}")
        except Exception as e:
            logging.error(f"[db] query error, userId={self.user_id}, lover_id={self.lover_id}, e={e}")
            await ws.close(code=1008, reason="Invalid user pair")
            return
        await ws.accept()
        # task = asyncio.create_task(heartbeat(ws))
        session_id = f'{self.user_id}_{self.lover_id}'
        try:
            while True:
                try:
                    # 用户发送消息
                    msg = await asyncio.wait_for(
                        ws.receive(),
                        timeout=65.0  # 必须 > 心跳间隔
                    )
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
                    full_response = await self.generate_and_save(query=user_text, session_id=session_id)
                    print(full_response)
                    await ws.send_text(full_response)
                except asyncio.TimeoutError:
                    logging.error(f"Client timeout, closing connection")
                    break
        except Exception as e:
            logging.error(f"[ws] connect error={e}")
            return
        # finally:
        # task.cancel()

    def get_prompt(self):
        prompt_text = mapper.get_active_prompt(self.lover_id).prompt_text
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

    def get_session_history(self, session_id: str) -> PostgresChatMessageHistoryAsync:
        return PostgresChatMessageHistoryAsync(session_id=session_id)

    async def generate_and_save(self, query: str, session_id: str) -> str:
        prompt = self.get_prompt()
        chain = prompt | self.model
        with_message_history = RunnableWithMessageHistory(
            chain,
            self.get_session_history,  # 现在返回的是异步历史对象
            input_messages_key="messages"
        )
        config = {"configurable": {"session_id": session_id}}
        chunks = await with_message_history.ainvoke(
            {"messages": [HumanMessage(content=query)]},
            config=config
        )
        print(chunks)
        full_response = chunks.content if hasattr(chunks, 'content') else str(chunks)
        logging.info(f'full response={full_response}')
        # 保存历史记录
        await save_messages(
            session_id=session_id,
            messages=[HumanMessage(content=query), AIMessage(content=full_response)]
        )
        return full_response

    async def update_profile(self, lover_image: models.LoverAvatarRequest) -> models.LoverAvatarRes:
        try:
            local_path = await self.profile_generate(lover_image.prompt)
            profile_url = await self.profile_upload(local_path)
            logging.info(f'generate image url={profile_url}')
            model = models.LoverAvatarRes(
                user_id=lover_image.user_id,
                lover_id=lover_image.lover_id,
                avatar=profile_url
            )
            return model
        except consts.ServiceError as e:
            raise e

    async def profile_generate(self, prompt: str):
        generator = ImageGenerate(self.user_id, self.lover_id, prompt)
        # 生成图像
        try:
            local_path = await generator.text_to_image()
        except consts.ServiceError as e:
            raise e
        return local_path

    async def profile_upload(self, local_path: str) -> str:
        # 上传图片
        comer = CosService(self.user_id, self.lover_id)
        try:
            await comer.upload_profile(local_path)
            url = comer.get_download_url()
            if os.path.exists(local_path):
                os.remove(local_path)
                logging.info(f'remove local image={local_path}')
            # 写db
            lover = models.UserLoverCreate()
            lover.avatar = url
            mapper.update_user_lover(self.user_id, self.lover_id, lover)
        except consts.ServiceError as e:
            raise e
        return url
