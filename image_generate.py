from huggingface_hub import AsyncInferenceClient
import asyncio

client = AsyncInferenceClient(
    token='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'
)
async def text_to_image():
    image = await client.text_to_image("An astronaut riding a horse on the moon.")
    image.save("astronaut.png")

if __name__ == '__main__':
    asyncio.run(text_to_image())


