# zimage_simple.py
from diffusers import DiffusionPipeline
import torch
import time


class SimpleZImage:
    def __init__(self, model_path):
        self.model_path = model_path
        self.pipe = None

    def load(self):
        """加载一次，多次使用"""
        if self.pipe is None:
            print("加载模型...")
            start = time.time()

            self.pipe = DiffusionPipeline.from_pretrained(
                self.model_path,
                torch_dtype=torch.float32,
                trust_remote_code=True
            )
            self.pipe = self.pipe.to("cpu")

            print(f"✅ 加载完成，耗时: {time.time() - start:.1f}秒")

        return self.pipe

    def generate(self, prompt, **kwargs):
        """生成图片"""
        if self.pipe is None:
            self.load()

        # 生成
        result = self.pipe(prompt, **kwargs)

        # 提取图片
        if hasattr(result, 'images'):
            return result.images[0]
        elif isinstance(result, dict) and 'images' in result:
            return result['images'][0]
        return result


# 使用
if __name__ == "__main__":
    generator = SimpleZImage("/Users/zhuangruiying/.cache/modelscope/hub/Tongyi-MAI/Z-Image-Turbo")

    # 第一次生成（会加载模型）
    img1 = generator.generate(
        "一只猫",
        num_inference_steps=4,
        height=512,
        width=512
    )
    img1.save("cat1.png")

    # 第二次生成（模型已加载，很快）
    img2 = generator.generate(
        "一只狗",
        num_inference_steps=4
    )
    img2.save("dog1.png")
