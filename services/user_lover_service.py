import asyncio
import logging

import consts
import db
import models
import mapper
from fastapi import WebSocket, WebSocketDisconnect




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
                message = await asyncio.wait_for(
                    ws.receive(),
                    timeout=65.0  # 必须 > 心跳间隔
                )
                #todo:1. 存储历史消息

                #todo:2.请求ai

                #todo:3.发送ai response


            except asyncio.TimeoutError:
                logging.error(f"Client timeout, closing connection")
                break
    except Exception as e:
        logging.error(f"[ws] connect error={e}")
        return
    finally:
        task.cancel()
        await ws.close()

