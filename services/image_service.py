# 豆包大模型生成头像
import logging

import requests

import mapper
import models
from models import LoverAvatarRes
from settings import settings
from consts import ServiceError, ErrorCode

"""
使用豆包API生成图片

Args:
    prompt: 图片描述文本
Returns:
    包含生成结果的字典
"""


def generate_image_with_doubao(prompt: str) -> str:
    # 获取API密钥
    api_key, url = settings.get_doubao_conf
    # 请求头
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    # 请求体
    payload = {
        "model": "doubao-seedream-4-5-251128",
        "prompt": prompt,
        "sequential_image_generation": "disabled",
        "response_format": "url",
        "size": "2K",
        "stream": False,
        "watermark": True
    }
    try:
        logging.info("🔄 发送请求到豆包API...")
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        # 检查响应状态
        if response.status_code == 200:
            result = response.json()
            if "data" in result and len(result["data"]) > 0:
                image_url = result["data"][0].get("url")
                if image_url:
                    logging.info(f"📸 图片生成成功: {image_url}")
                    return image_url
                else:
                    logging.error("⚠️  未找到图片URL")
                    raise ServiceError(ErrorCode.IMAGE_GENERATE_ERR)
            else:
                logging.error("⚠️  响应中没有图片数据")
                raise ServiceError(ErrorCode.IMAGE_GENERATE_ERR)
        elif response.status_code == 401:
            error_data = response.json()
            error_code = error_data.get("error", {}).get("code", "Unknown")
            error_msg = error_data.get("error", {}).get("message", "Unknown error")
            logging.error(f"❌ 认证失败 ({error_code}): {error_msg}")
            raise ServiceError(ErrorCode.IMAGE_GENERATE_ERR)
        else:
            raise ServiceError(ErrorCode.IMAGE_GENERATE_ERR)

    except requests.exceptions.RequestException as e:
        logging.error(f'request to doubao api error={e}')
        raise ServiceError(ErrorCode.IMAGE_GENERATE_ERR)


def generate_profile(lover_id, user_id, prompt: str) -> LoverAvatarRes:
    if len(lover_id) == 0 or len(user_id) == 0 or len(prompt) == 0:
        raise ServiceError(ErrorCode.PARAM_ERR)
    try:
        url = generate_image_with_doubao(prompt)
        logging.info(f'lover avatar={url}')
        if url is not None:
            mapper.update_user_lover_avatar(user_id, lover_id, url)
            model = models.LoverAvatarRes(
                user_id=user_id,
                lover_id=lover_id,
                avatar=url
            )
            return model
    except ServiceError as e:
        raise e
    except Exception as e:
        logging.error(f'update profile error={e}')
        raise ServiceError(ErrorCode.DB_ERR)
