from typing import List
from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain_classic.memory import ConversationBufferMemory
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langchain_core.callbacks import StdOutCallbackHandler
from langchain_core.prompts import PromptTemplate
from langchain_ollama import OllamaLLM
from langchain_core.tools import BaseTool

import tools
from mapper import PostgresChatMessageHistoryAsync


class PersonalityLoverAgent:
    """DuckDuckGo搜索 + Ollama本地模型的Agent (带敏感词过滤)"""

    def __init__(self,
                 model_name: str = "llama3.1",
                 temperature: float = 0.7,
                 max_tokens: int = 1024):

        # 1. 初始化 Ollama LLM
        self.llm = OllamaLLM(
            model=model_name,
            base_url="http://localhost:11434",
            temperature=temperature,
            num_predict=max_tokens
        )

        # 定义敏感词列表
        self.sensitive_words = [
            "色情", "赌博", "暴力", "恐怖主义",
            "敏感政治词汇", "非法交易", "作弊",
            # 在这里添加更多敏感词
        ]

        # 2. 创建工具
        self.tools = self._create_tools()

        # 3. 基础 Prompt 模板
        self.base_prompt_template = self._build_personalized_prompt()

    def _create_tools(self) -> List[BaseTool]:
        """创建工具列表"""
        search_wrapper = DuckDuckGoSearchAPIWrapper(region="cn-zh", time="y", max_results=5)

        # 实例化自定义工具类
        search_tool = tools.FilteredSearchTool(
            search_wrapper=search_wrapper,
            sensitive_words=self.sensitive_words
        )
        return [search_tool]

    def _build_personalized_prompt(self) -> PromptTemplate:
        full_template = """You are a helpful assistant with the following persona:
    {persona}
 
    You have access to the following tools:
    {tools}
    # CRITICAL INSTRUCTIONS (关键指令)
    1. **Tool Usage**: Use tools ONLY when you lack information.
    2. **Termination**: As soon as you have enough information to answer the user's question, you MUST stop using tools.
    3. **Formatting**: 
       - Do NOT output any conversational text (like "Okay", "Let me see", "Baby") between 'Observation' and 'Thought'.
       - All your personality, humor, and conversational tone must appear ONLY in the 'Final Answer' section.
       - The sequence MUST be: Thought -> Action -> Action Input -> Observation -> Thought -> Final Answer.
       - Once you start 'Final Answer', do NOT output any more 'Action' or 'Thought'.

    Use the following format strictly:
    Question: the input question you must answer
    Thought: you should always think about what to do
    Action: the action to take, should be one of [{tool_names}]
    Action Input: the input to the action as a valid JSON string
    Observation: the result of the action
    ... (this Thought/Action/Action Input/Observation can repeat N times)
    Thought: I now know the final answer
    Final Answer: the final answer to the original input question

    Begin!

    Previous conversation history:
    {chat_history}

    Question: {input}
    {agent_scratchpad}"""

        return PromptTemplate(
            template=full_template,
            input_variables=[
                "persona", "tools", "tool_names", "chat_history", "input", "agent_scratchpad"
            ]
        )

    def get_session_history(self, session_id: str):
        return PostgresChatMessageHistoryAsync(session_id=session_id)

    async def run(self, query: str, session_id: str, persona_text: str):
        all_tool = self.tools
        tool_names = [tool.name for tool in all_tool]

        print("=== DEBUG: Available Tool Names ===")
        print(tool_names)
        current_time = tools.get_current_time()
        persona_text = f'今天的日期是{current_time},以下请基于当前时间回答问题,{persona_text}'
        final_prompt = self.base_prompt_template.partial(
            persona=persona_text,
            tools="\n".join([f"{tool.name}: {tool.description}" for tool in all_tool]),
            tool_names=", ".join(tool_names)
        )

        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )

        try:
            # 创建智能体
            agent = create_react_agent(
                llm=self.llm,
                tools=all_tool,
                prompt=final_prompt
            )

            # 创建执行器
            agent_executor = AgentExecutor(
                agent=agent,
                tools=all_tool,
                memory=memory,
                verbose=True,
                handle_parsing_errors=True,
                max_iterations=5,
                callbacks=[StdOutCallbackHandler()]
            )

            print(f"=== DEBUG: Executing query: {query} ===")

            result = await agent_executor.ainvoke({
                "input": query,
                "chat_history": memory.buffer
            })

            return result.get("output", str(result))

        except Exception as e:
            print(f"=== ERROR DETAILS ===")
            import traceback
            traceback.print_exc()
            return f"智能体执行出错：{str(e)}"
