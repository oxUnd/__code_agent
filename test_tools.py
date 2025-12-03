import os
from tools import AgentTools

def test_tools():
    print("Testing tools...")
    
    # Test 1: Write File
    test_file = "test_file.txt"
    content = "Hello\nWorld"
    print(f"Testing write_file to {test_file}...")
    result = AgentTools.write_file.invoke({"path": test_file, "content": content})
    print(result)
    assert os.path.exists(test_file)
    with open(test_file, 'r') as f:
        assert f.read() == content
    print("PASS: write_file")

    # Test 2: Read File
    print("Testing read_file...")
    read_content = AgentTools.read_file.invoke({"path": test_file})
    assert read_content == content
    print("PASS: read_file")

    # Test 3: Generate Diff
    print("Testing generate_diff...")
    new_content = "Hello\nWorld\nModified"
    diff = AgentTools.generate_diff.invoke({"path": test_file, "new_content": new_content})
    print(f"Diff output:\n{diff}")
    assert "+Modified" in diff
    print("PASS: generate_diff")

    # Test 4: Scan Directory
    print("Testing scan_directory...")
    scan_result = AgentTools.scan_directory.invoke({"path": "."})
    print(f"Scan result:\n{scan_result}")
    assert test_file in scan_result
    print("PASS: scan_directory")

    # Test 5: Run Command
    print("Testing run_command...")
    cmd_result = AgentTools.run_command.invoke({"command": "echo 'test command'"})
    print(f"Command result: {cmd_result}")
    assert "test command" in cmd_result
    print("PASS: run_command")

    # Cleanup
    os.remove(test_file)
    print("All tests passed!")

if __name__ == "__main__":
    test_tools()
