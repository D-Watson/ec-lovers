from langchain_core.messages import HumanMessage,SystemMessage
from langchain_ollama.chat_models import ChatOllama

model = ChatOllama(
    model="llama3.1",
    temperature=0,
    # other params...
)
messages = [
    SystemMessage(
       content="You are a helpful assistant that translates English to French. Translate the user sentence."
    ),
    HumanMessage(content="I love programming."),
]
ai_msg = model.invoke(messages)