import re
from typing import List, Type, Any
from langchain_core.tools import BaseTool
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from pydantic import BaseModel, Field, PrivateAttr


# 定义输入模型
class SearchInput(BaseModel):
    query: str = Field(description="需要搜索的关键词或问题")


class FilteredSearchTool(BaseTool):
    """自定义搜索工具：包含敏感词过滤和调试日志"""

    # 1. 定义标准字段 (会在 Tool 描述中显示)
    name: str = "duckduckgo_search"
    description: str = "搜索互联网获取最新实时信息。输入应为具体的搜索关键词。如果用户询问新闻、天气、股价等实时信息，请使用此工具。"
    args_schema: Type[BaseModel] = SearchInput

    # 2. 定义私有属性 (不会导致 Pydantic 报错，用于存储内部状态)
    # 使用 PrivateAttr() 告诉 Pydantic 这些不是模型字段，而是普通实例变量
    _search_wrapper: DuckDuckGoSearchAPIWrapper = PrivateAttr()
    _sensitive_words: List[str] = PrivateAttr()
    _clean_regex: Any = PrivateAttr()

    def __init__(self, search_wrapper: DuckDuckGoSearchAPIWrapper, sensitive_words: List[str], **kwargs):
        # 初始化父类 (设置 name, description 等)
        super().__init__(**kwargs)

        # 初始化私有属性
        self._search_wrapper = search_wrapper
        self._sensitive_words = sensitive_words
        self._clean_regex = re.compile(r'\s+')

    def _filter_content(self, text: str) -> str:
        """内部过滤方法"""
        if not text:
            return ""

        # 1. 基础清洗
        text = self._clean_regex.sub(' ', text).strip()

        # 2. 敏感词过滤
        filtered_count = 0
        for word in self._sensitive_words:
            if word in text:
                text = text.replace(word, "***")
                filtered_count += 1

        # 3. 移除广告标记
        text = re.sub(r'\[.*?广告.*?\]', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\(.*?推广.*?\)', '', text, flags=re.IGNORECASE)

        if filtered_count > 0:
            print(f"⚠️ [FILTER] 已过滤 {filtered_count} 个敏感词片段。")

        return text

    def _run(self, query: str) -> str:
        """同步执行方法"""
        return self._execute_search(query)

    async def _arun(self, query: str) -> str:
        """异步执行方法"""
        return self._execute_search(query)

    def _execute_search(self, query: str) -> str:
        """实际执行搜索和过滤的逻辑"""
        print(f"\n🔍 [SEARCH TOOL] 正在搜索: {query}")
        try:
            raw_result = self._search_wrapper.run(query)

            if not raw_result or len(raw_result.strip()) == 0:
                return "没有找到相关信息。"

            print(f"📄 [RAW RESULT LENGTH]: {len(raw_result)} chars")
            print(f"📄 [RAW RESULT PREVIEW]: {raw_result[:300]}...")

            # 执行过滤
            clean_result = self._filter_content(raw_result)

            print(f"✨ [CLEAN RESULT LENGTH]: {len(clean_result)} chars")
            print(f"✨ [CLEAN RESULT PREVIEW]: {clean_result[:300]}...")

            if not clean_result:
                return "搜索结果包含大量无效内容，已自动过滤，暂无有效信息。"

            return f"搜索结果: {clean_result}"

        except Exception as e:
            error_msg = f"搜索出错: {str(e)}"
            print(f"❌ [SEARCH ERROR]: {error_msg}")
            return error_msg
