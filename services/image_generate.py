import logging
import os

from huggingface_hub import AsyncInferenceClient
import asyncio

import consts


class ImageGenerate(object):

    client: AsyncInferenceClient
    user_id: str
    lover_id: str
    prompt: str

    def __init__(self, user_id: str, lover_id: str, prompt: str):
        self.aclient = AsyncInferenceClient(token=os.getenv('HUGGINGFACEW_HUB'))
        self.user_id = user_id
        self.lover_id = lover_id
        self.prompt = prompt

    async def text_to_image(self) -> str:
        try:
            image = await self.client.text_to_image(self.prompt)
            path = f'{self.user_id}/{self.lover_id}.png'
            image.save(path)
            return path
        except Exception as e:
            logging.error(f'generate image error, e={e}')
            raise consts.ServiceError(consts.ErrorCode.HUGGING_GENERATE_ERR)


if __name__ == '__main__':
    img = ImageGenerate('', '', '')
    asyncio.run(img.text_to_image())
