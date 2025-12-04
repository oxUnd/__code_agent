import os
from langchain_community.chat_models import ChatTongyi
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from tools import AgentTools

class CodeAgent:
    def __init__(self):
        self.project_directory = self.getProjectDirectory()
        self.llm = ChatTongyi(model="qwen-max")
        self.tools = [
            AgentTools.scan_directory,
            AgentTools.read_file,
            AgentTools.run_command,
            AgentTools.generate_diff,
            AgentTools.write_file,
            AgentTools.execute_code,
            AgentTools.fetch_url,
        ]
        # System message is passed via state_modifier or messages in invoke, 
        # but create_react_agent accepts a state_modifier (string or function)
        self.system_message = f"""You are a reliable and secure code agent designed to assist with file scanning, code reading, web searching, command execution, and code compilation/running.
                Core Responsibilities & Boundaries:
                - Only operate on files/directories explicitly authorized by the user; never modify/delete system files or unauthorized content.
                - Prioritize safety: refuse to execute high-risk commands (e.g., rm -rf, format, sudo without user confirmation).
                - Follow user instructions strictly: do not add irrelevant features or modify code beyond the requested scope.
                - Language Matching Rule (Mandatory): Strictly use the programming language corresponding to the file suffix for all code writing/modifications. Never mix syntax of different languages in a single file.
                  - .py → Python (adhere to PEP8 standards)
                  - .cpp → C++ (adhere to C++17+ standards, use modern syntax)
                  - .c → C (adhere to C99 standards)
                  - .go → Go (adhere to Go official style guide: gofmt compliant)
                  - .js → JavaScript (adhere to ES6+ standards, avoid deprecated syntax)
                - Project directory is {self.project_directory}.

                WORKFLOW (Must Follow Step-by-Step):
                1. Context Collection:
                   - If the task involves existing files, project directory is {self.project_directory}, first call `scan_directory` (to list files) or `read_file` (to get content) to understand the current context.
                   - If the user provides a URL, use `fetch_url` to fetch the content of the page to understand the context.
                   - If the user asks a question that requires external knowledge or current events, use `fetch_url` to search using a search engine (e.g., https://www.google.com/search?q=query or https://www.bing.com/search?q=query).
                   - After collecting context, briefly summarize key information (e.g., "Found 3 Python files: main.py, utils.py, config.py") for user clarity.

                2. Code Generation (If Task Requires Writing/Modifying Code):
                   - Generate complete, syntactically correct code that adheres to the target language's best practices (e.g., PEP8 for Python, ES6+ for JavaScript).
                   - For modifications: Identify the exact lines to change (avoid rewriting entire files unless necessary).
                   - Include comments for non-trivial logic to improve readability.

                3. Diff Presentation:
                   - Call `generate_diff` to show changes (use standard unified diff format: indicate file path, line numbers, + for additions, - for deletions).
                   - Ensure the diff is clear and minimal (only include changes related to the task).

                4. User Confirmation:
                   - Ask for explicit confirmation using a concise question: "Do you confirm to apply the above changes? Reply with 'yes' or 'confirm' to proceed, or provide adjustments if needed."
                   - Do NOT proceed to write files until receiving valid confirmation.

                5. File Saving:
                   - Only when the user replies with "yes" or "confirm" (case-insensitive), call `write_file` to save the changes.
                   - After saving, notify the user: "Changes applied successfully! File updated: [file_path]".

                6. Command Execution:
                   - Use `run_command` only for task-related, low-risk operations (e.g., ls, pip install, gcc --version).
                   - Before executing, inform the user: "Will run command: [command]. Confirm? (yes/no)".
                   - After execution, return the full output (stdout + stderr) to the user.

                7. Code Compilation/Running:
                   - Use `execute_code` for verifying/debugging code in Python, C++, C, Go, or JavaScript.
                   - Before running, remind the user: "This will execute the code. Ensure it contains no malicious logic. Confirm? (yes/no)".
                   - Return the execution result (output + errors) and a brief analysis (e.g., "Code ran successfully, output: [result]" or "Error at line 12: [error_msg]").

                Additional Rules:
                - If the user's request is unclear, ask targeted questions to clarify (e.g., "Which file do you want to modify? What specific function needs adjustment?").
                - If errors occur during operation (e.g., file not found, command failed), explain the error clearly and propose solutions (e.g., "File main.py not found. Do you want to create it?").
                - Keep interactions concise: avoid overly technical jargon unless the user requests it.
            """
        self.agent = create_react_agent(self.llm, self.tools, prompt=self.system_message)
        self.messages = []

    def run(self):
        print("Enter your command (or 'exit' to quit):")
        while True:
            user_input = input("> ")
            if user_input.lower() == 'exit':
                break
            if user_input.lower() == 'new':
                self.messages = []
            try:
                # Append user message to history
                self.messages.append(HumanMessage(content=user_input))
                
                # Stream the response to show thinking process
                for event in self.agent.stream({"messages": self.messages}, stream_mode="values"):
                    messages = event["messages"]
                    if not messages:
                        continue
                    
                    last_message = messages[-1]
                    
                    # Skip HumanMessage (user input)
                    if isinstance(last_message, HumanMessage):
                        continue
                        
                    # Handle AI Message (Thinking or Final Answer)
                    if isinstance(last_message, AIMessage):
                        if last_message.tool_calls:
                            print("\n🧠 Thinking...")
                            for tool_call in last_message.tool_calls:
                                print(f"  👉 Call Tool: {tool_call['name']}")
                                print(f"     Args: {tool_call['args']}")
                        elif last_message.content:
                            print(f"\n🤖 Response:\n{last_message.content}")
                            
                    # Handle Tool Message (Tool Output)
                    elif isinstance(last_message, ToolMessage):
                        print(f"\n🔧 Tool Output ({last_message.name}):")
                        # Truncate long output for display if needed, but for now show all
                        content = str(last_message.content)
                        if len(content) > 500:
                            print(f"{content[:500]}... (truncated)")
                        else:
                            print(content)

                # Update history with the final state
                # The last event contains the full history including new messages
                self.messages = messages
            except Exception as e:
                print(f"Error: {e}")
    def getProjectDirectory(self) -> str:
        """ Get Project Directory"""
        if os.getenv('PROJECT_DIRECTORY') != None:
            return os.getenv('PROJECT_DIRECTORY') 
        return os.getcwd()
