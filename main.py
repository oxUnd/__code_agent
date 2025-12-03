import os
from dotenv import load_dotenv
from agent import CodeAgent

def main():
    load_dotenv()
    print("Code Agent Initialized")
    # TODO: Initialize and run agent
    agent = CodeAgent()
    agent.run()

if __name__ == "__main__":
    main()
