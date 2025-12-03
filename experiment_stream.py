from dotenv import load_dotenv
load_dotenv()
from langchain_community.chat_models import ChatTongyi
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool

@tool
def magic_number_tool(input: int) -> int:
    """Returns the magic number."""
    return input * 42

llm = ChatTongyi(model="qwen-max")
tools = [magic_number_tool]
agent = create_react_agent(llm, tools)

print("--- Starting Stream ---")
for event in agent.stream({"messages": [HumanMessage(content="What is the magic number for 2?")]}, stream_mode="values"):
    print(f"Event: {event}")
    if "messages" in event:
        print(f"Last Message: {event['messages'][-1]}")
print("--- End Stream ---")
