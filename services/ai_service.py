import asyncio

from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import (
    BaseChatMessageHistory,
    InMemoryChatMessageHistory,
)
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


model = ChatOllama(
    model="llama3.1",
    temperature=0,
    # other params...
)
store = {}
promt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant. Answer all questions to the best of your ability,and please use the {language} language to answer.",
        ),
        MessagesPlaceholder(variable_name="messages")
    ]
)
chain = promt | model

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

with_message_history = RunnableWithMessageHistory(chain, get_session_history,input_messages_key="messages")
config = {
    "configurable": {"session_id":"cookie1"}
}
response = with_message_history.invoke(
    {"messages":[HumanMessage(content="Hi, I'm cookie,I like dancing and writing.")],
     "language": "Italy"},
    config=config,
)

async def generate():
    async for chunk in with_message_history.astream(
            {"messages": [HumanMessage(content="Please give me some suggest according to my hobbies.")], "language": "Chinese"},
            config=config
    ):
        yield f"{chunk.content}"

async def main():
    async for chunk in generate():
        print(chunk,end=' ')


if __name__ == "__main__":
    asyncio.run(main())