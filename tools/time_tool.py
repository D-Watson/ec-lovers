from typing import Any, Type, Optional, Dict
from datetime import datetime
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool


class TimeToolInput(BaseModel):
    """时间工具不需要输入参数"""
    pass


class TimeTool(BaseTool):
    """获取当前日期和时间的工具"""

    name: str = "get_current_time"
    description: str = "获取当前的日期和时间，格式为 YYYY年MM月DD日 HH:MM:SS。此工具不需要任何输入参数。"
    args_schema: Type[BaseModel] = TimeToolInput
    return_direct: bool = False

    def _run(
            self,
            *args: Any,
            **kwargs: Any,
    ) -> str:
        """同步执行：获取当前时间"""
        return self._get_current_time()

    async def _arun(
            self,
            *args: Any,
            **kwargs: Any,
    ) -> str:
        """异步执行：获取当前时间"""
        return self._get_current_time()

    def _get_current_time(self) -> str:
        """获取当前时间的核心方法"""
        now = datetime.now()
        # 中文格式，更友好
        return now.strftime("%Y年%m月%d日 %H:%M:%S")

    # 可选：添加时区支持
    def _get_current_time_with_timezone(self, timezone: str = "Asia/Shanghai") -> str:
        """获取带时区的当前时间"""
        from datetime import datetime
        import pytz

        try:
            tz = pytz.timezone(timezone)
            now = datetime.now(tz)
            return now.strftime("%Y年%m月%d日 %H:%M:%S %Z")
        except:
            # 如果时区失败，返回本地时间
            return self._get_current_time()


def get_current_time() -> str:
    """外部调用接口：获取当前时间"""
    tool = TimeTool()
    return tool._get_current_time()
