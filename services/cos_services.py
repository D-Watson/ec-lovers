# -*- coding=utf-8
import logging
import os
from qcloud_cos.cos_exception import CosClientError, CosServiceError
from settings import settings
import consts


class CosService(object):

    def __init__(self, user_id, lover_id,):
        self.client = settings.get_cos_client()
        self.user_id = user_id
        self.lover_id = lover_id

    async def upload_profile(self, path: str):
        file_name = f'{self.user_id}/{self.lover_id}.png'
        # 使用高级接口断点续传，失败重试时不会上传已成功的分块(这里重试3次)
        for i in range(0, 3):
            try:
                response = self.client.upload_file(
                    Bucket=os.getenv('PROFILE_BUCKET'),
                    Key=file_name,
                    LocalFilePath=path,
                    EnableMD5=False,
                    progress_callback=None)
                logging.info(f'upload file success, res={response}')
                break
            except CosClientError or CosServiceError as e:
                logging.error(f'upload file error={e}')
                raise consts.ServiceError(consts.ErrorCode.COS_UPLOAD_ERR)

    def get_download_url(self) -> str:
        file_name = f'{self.user_id}/{self.lover_id}.png'
        # 生成下载 URL，使用临时密钥签名
        try:
            url = self.client.get_presigned_download_url(
                Bucket=os.getenv('PROFILE_BUCKET'),
                Key=file_name
            )
            return url
        except Exception as e:
            logging.error(f'get download url error={e}')
            raise consts.ServiceError(consts.ErrorCode.COS_DOWNLOAD_ERR)


