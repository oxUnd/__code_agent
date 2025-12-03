from langchain_community.chat_models import ChatTongyi
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage
from tools import AgentTools

class CodeAgent:
    def __init__(self):
        self.llm = ChatTongyi(model="qwen-max")
        self.tools = [
            AgentTools.scan_directory,
            AgentTools.read_file,
            AgentTools.run_command,
            AgentTools.generate_diff,
            AgentTools.write_file,
            AgentTools.execute_code
        ]
        # System message is passed via state_modifier or messages in invoke, 
        # but create_react_agent accepts a state_modifier (string or function)
        self.system_message = """You are a helpful code agent. You can scan files, read code, execute commands, and compile/run code.
            
            WORKFLOW:
            1. Scan the directory or read files to understand the context.
            2. When asked to write code, first generate the code internally.
            3. Call `generate_diff` to show the changes to the user.
            4. ASK the user for confirmation.
            5. ONLY if the user says "yes" or "confirm", call `write_file` to save the changes.
            6. You can use `run_command` to run system commands.
            7. You can use `execute_code` to compile and run code in Python, C++, C, Go, or JavaScript. This is useful for debugging or verifying code.
            """
        self.agent = create_react_agent(self.llm, self.tools, prompt=self.system_message)
        self.messages = []

    def run(self):
        print("Enter your command (or 'exit' to quit):")
        while True:
            user_input = input("> ")
            if user_input.lower() == 'exit':
                break
            if use_input.lower() == 'new':
                self.messages = []
            try:
                # Append user message to history
                self.messages.append(HumanMessage(content=user_input))
                
                # LangGraph agent expects a list of messages or a dict with "messages"
                response = self.agent.invoke({"messages": self.messages})
                
                # The response is the state, which contains "messages"
                # We want to print the last message content if it's from AI
                messages = response["messages"]
                if messages:
                    last_message = messages[-1]
                    print(last_message.content)
                    # Append agent response to history
                    self.messages.append(last_message)
            except Exception as e:
                print(f"Error: {e}")
            except Exception as e:
                print(f"Error: {e}")
