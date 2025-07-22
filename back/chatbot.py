# chatbot.py

from typing import List, Dict
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables.base import Runnable
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from langchain_core.chat_history import BaseChatMessageHistory 
from langchain_community.chat_message_histories import ChatMessageHistory
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("❌ GOOGLE_API_KEY not found in .env")

# Initialize LLM
llm = ChatGoogleGenerativeAI(
    model="models/gemini-2.5-pro",
    google_api_key=GOOGLE_API_KEY
)

# Prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful medical assistant. Respond clearly and concisely."),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}")
])
chain: Runnable = prompt | llm

# 🧠 Store chat history objects per session
# Changed to store the BaseChatMessageHistory directly, not ConversationBufferMemory
session_store: Dict[str, BaseChatMessageHistory] = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    """
    Returns the chat history object for a given session ID.
    If no history exists, it creates a new InMemoryChatMessageHistory.
    """
    if session_id not in session_store:
        session_store[session_id] = ChatMessageHistory() # Use ChatMessageHistory directly
    return session_store[session_id]

# Wrap chain with memory
chat_chain = RunnableWithMessageHistory(
    chain,
    # This lambda now returns BaseChatMessageHistory, which is what RunnableWithMessageHistory expects
    lambda session_id: get_session_history(session_id),
    input_messages_key="input",
    history_messages_key="chat_history"
)

def query_gemini_from_messages(messages: List[Dict[str, str]], session_id: str) -> str:
    # Ensure the messages list always ends with a user message for the current turn.
    # The `RunnableWithMessageHistory` will handle storing these in the session history.
    last_user_message_content = next((msg["content"] for msg in reversed(messages) if msg["role"] == "user"), None)
    if not last_user_message_content:
        raise ValueError("No user message found in payload for current turn.")

    result = chat_chain.invoke(
        {"input": last_user_message_content},
        config={"configurable": {"session_id": session_id}}
    )

    return result.content

def reset_session_memory(session_id: str):
    """
    Resets the chat history for a given session.
    """
    if session_id in session_store:
        session_store[session_id].clear() # Call clear on the BaseChatMessageHistory object