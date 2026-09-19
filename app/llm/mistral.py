from langchain_ollama import ChatOllama


MODEL_NAME = "mistral:latest"


llm = ChatOllama(
    model=MODEL_NAME,
    temperature=0,
)