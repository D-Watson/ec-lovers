# metrics.py
from prometheus_client import Counter, Histogram

# 请求计数器：按 method, path, status 分组
REQUEST_COUNT = Counter(
    "fastapi_request_count",
    "Total number of requests",
    ["method", "path", "status"]
)

# 请求延迟直方图
REQUEST_LATENCY = Histogram(
    "fastapi_request_latency_seconds",
    "Request latency in seconds",
    ["method", "path"]
)
