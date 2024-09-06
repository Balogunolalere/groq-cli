import pytest
import json
import subprocess
from unittest.mock import patch, MagicMock
from groq_cli import (
    get_commands,
    handle_error,
    execute_command,
    display_and_select_command,
    display_and_select_solution,
)


# Mock the Groq client for testing
@patch("groq_cli.client.chat.completions.create")
def test_get_commands(mock_create):
    mock_create.return_value = MagicMock(
        choices=[
            MagicMock(
                message=MagicMock(
                    content=json.dumps(
                        {
                            "commands": [
                                {
                                    "command": "ls -la",
                                    "description": "List all files in the current directory",
                                    "installation": "",
                                }
                            ]
                        }
                    )
                )
            )
        ]
    )

    query = "list all files"
    result = get_commands(query)

    assert isinstance(result, dict)
    assert "commands" in result
    assert len(result["commands"]) > 0
    assert "command" in result["commands"][0]
    assert "description" in result["commands"][0]
    assert "installation" in result["commands"][0]


@patch("groq_cli.client.chat.completions.create")
def test_handle_error(mock_create):
    mock_create.return_value = MagicMock(
        choices=[
            MagicMock(
                message=MagicMock(
                    content=json.dumps(
                        {
                            "explanation": "The 'ls' command is not found.",
                            "solutions": [
                                {
                                    "description": "Install coreutils package",
                                    "command": "sudo apt-get install coreutils",
                                }
                            ],
                        }
                    )
                )
            )
        ]
    )

    error_message = "ls: command not found"
    result = handle_error(error_message)

    assert isinstance(result, dict)
    assert "explanation" in result
    assert "solutions" in result
    assert len(result["solutions"]) > 0
    assert "description" in result["solutions"][0]
    assert "command" in result["solutions"][0]


@patch("subprocess.run")
def test_execute_command(mock_run):
    mock_run.return_value = MagicMock(stdout="Output of the command", returncode=0)

    command = "ls -la"
    success = execute_command(command)

    assert success is True
    mock_run.assert_called_once_with(
        ["bash", "-c", command], check=True, text=True, capture_output=True
    )


if __name__ == "__main__":
    pytest.main()
