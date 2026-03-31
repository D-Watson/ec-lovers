
async def react_flow():
    """测试完整的 ReAct 流程"""
    print("=== 开始测试 ReAct 流程 ===")

    # 1. 先确认搜索工具能工作
    from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
    search_wrapper = DuckDuckGoSearchAPIWrapper(region="cn-zh", time="y", max_results=2)

    test_query = "上海今天天气"
    search_result = search_wrapper.run(test_query)
    print(f"✓ 搜索工具测试成功")
    print(f"搜索 '{test_query}' 结果前200字符:")
    print(f"{search_result[:200]}...")
    print("="*60)

    # 2. 测试 LLM
    from langchain_ollama import OllamaLLM
    llm = OllamaLLM(
        model="llama3.1",
        base_url="http://localhost:11434",
        temperature=0.1,  # 降低温度以获得稳定输出
        num_predict=512
    )

    print("测试 LLM 响应...")
    test_prompt = "请用一句话回复: 测试成功"
    llm_response = await llm.ainvoke(test_prompt)
    print(f"✓ LLM 测试成功: {llm_response}")
    print("="*60)

    # 3. 测试 ReAct 格式
    print("测试 LLM 的 ReAct 格式输出...")
    react_test_prompt = """你是一个AI助手，请按照以下格式回答：

Question: 今天上海天气如何？

请用以下格式思考：
Thought: 用户询问实时天气，我需要搜索
Action: duckduckgo_search
Action Input: {"query": "上海今天天气"}
Observation: <Result of the tool>
Thought: <Reasoning based on observation>
Final Answer: <Response>

请只输出 Thought/Action/Action Input/Observation/Final Answer，不要额外内容。"""

    react_response = await llm.ainvoke(react_test_prompt)
    print(f"ReAct 格式测试输出:")
    print(react_response)
    print("="*60)

    return True

if __name__ == '__main__':
    import asyncio
    asyncio.run(react_flow())
