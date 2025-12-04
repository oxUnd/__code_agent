from langchain.tools import tool
import os
import subprocess

class AgentTools:
    @staticmethod
    @tool
    def scan_directory(path: str) -> str:
        """Scans a directory and lists all files."""
        try:
            files = []
            for root, _, filenames in os.walk(path):
                for filename in filenames:
                    files.append(os.path.join(root, filename))
            return "\n".join(files)
        except Exception as e:
            return f"Error scanning directory: {e}"

    @staticmethod
    @tool
    def read_file(path: str) -> str:
        """Reads the content of a file."""
        try:
            with open(path, 'r') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {e}"

    @staticmethod
    @tool
    def run_command(command: str) -> str:
        """Executes a system command."""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            return f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        except Exception as e:
            return f"Error executing command: {e}"

    @staticmethod
    @tool
    def generate_diff(path: str, new_content: str) -> str:
        """Generates a diff between the existing file and new content."""
        import difflib
        try:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    old_content = f.read()
            else:
                old_content = ""
            
            diff = difflib.unified_diff(
                old_content.splitlines(keepends=True),
                new_content.splitlines(keepends=True),
                fromfile=f"a/{path}",
                tofile=f"b/{path}"
            )
            return "".join(diff)
        except Exception as e:
            return f"Error generating diff: {e}"

    @staticmethod
    @tool
    def write_file(path: str, content: str) -> str:
        """Writes content to a file. Use this ONLY after the user has confirmed the diff."""
        try:
            with open(path, 'w') as f:
                f.write(content)
            return f"Successfully wrote to {path}"
        except Exception as e:
            return f"Error writing file: {e}"

    @staticmethod
    @tool
    def execute_code(file_path: str, language: str = None) -> str:
        """
        Compiles and executes code based on the file extension or provided language.
        Supported languages: python, cpp, go, javascript.
        """
        try:
            if not os.path.exists(file_path):
                return f"Error: File {file_path} not found."

            if language is None:
                _, ext = os.path.splitext(file_path)
                ext = ext.lower()
                if ext == '.py':
                    language = 'python'
                elif ext in ['.cpp', '.cc', '.cxx']:
                    language = 'cpp'
                elif ext == '.c':
                    language = 'c'
                elif ext == '.go':
                    language = 'go'
                elif ext == '.js':
                    language = 'javascript'
                else:
                    return f"Error: Unsupported file extension {ext}. Please specify language."

            executed_commands = []
            if language == 'python':
                cmd = f"python3 {file_path}"
                executed_commands.append(cmd)
            elif language == 'cpp':
                output_path = file_path + ".out"
                compile_cmd = f"g++ {file_path} -o {output_path}"
                executed_commands.append(compile_cmd)
                compile_result = subprocess.run(compile_cmd, shell=True, capture_output=True, text=True)
                if compile_result.returncode != 0:
                    return f"Executed: {compile_cmd}\nCompilation Error:\n{compile_result.stderr}"
                cmd = f"./{output_path}" if not os.path.isabs(output_path) else output_path
                executed_commands.append(cmd)
            elif language == 'c':
                output_path = file_path + ".out"
                compile_cmd = f"gcc {file_path} -o {output_path}"
                executed_commands.append(compile_cmd)
                compile_result = subprocess.run(compile_cmd, shell=True, capture_output=True, text=True)
                if compile_result.returncode != 0:
                    return f"Executed: {compile_cmd}\nCompilation Error:\n{compile_result.stderr}"
                cmd = f"./{output_path}" if not os.path.isabs(output_path) else output_path
                executed_commands.append(cmd)
            elif language == 'go':
                cmd = f"go run {file_path}"
                executed_commands.append(cmd)
            elif language == 'javascript':
                cmd = f"node {file_path}"
                executed_commands.append(cmd)
            else:
                return f"Error: Unsupported language {language}"

            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            # Clean up compiled binary for C++ and C
            if (language == 'cpp' or language == 'c') and os.path.exists(output_path):
                os.remove(output_path)

            command_log = "\n".join([f"Executed: {c}" for c in executed_commands])
            return f"{command_log}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"

        except Exception as e:
            return f"Error executing code: {e}"

    @staticmethod
    @tool
    def fetch_url(url: str) -> str:
        """Fetches the content of a URL and returns the text."""
        import requests
        from bs4 import BeautifulSoup
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            text = soup.get_text()
            # Break into lines and remove leading/trailing space on each
            lines = (line.strip() for line in text.splitlines())
            # Break multi-headlines into a line each
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            # Drop blank lines
            text = '\n'.join(chunk for chunk in chunks if chunk)
            return text
        except Exception as e:
            return f"Error fetching URL {url}: {e}"
