from modelscope import snapshot_download

model_dir = snapshot_download(
    'Tongyi-MAI/Z-Image-Turbo'
)
print(f"模型已下载到: {model_dir}")
