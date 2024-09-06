import argparse
import os
import json
import sys
import termios
import tty
import subprocess
from groq import Groq
from dotenv import load_dotenv
import re

# Load environment variables from .env file
load_dotenv()

# Load API key from environment variable for better security
API_KEY = os.getenv('GROQ_API_KEY')
if not API_KEY:
    raise ValueError("GROQ_API_KEY environment variable not set")

client = Groq(api_key=API_KEY)

def get_commands(query):
    completion = client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": """
                You are an expert Linux command-line interface (CLI) master, capable of providing the most appropriate and efficient commands for any operation across various Linux distributions and tools. Your expertise covers a wide range of domains including but not limited to:

                    1. File and directory operations (e.g., ls, cp, mv, rm, mkdir, find, grep)
                    2. System administration (e.g., systemctl, journalctl, useradd, passwd)
                    3. Network operations (e.g., ip, ss, netstat, ping, traceroute, nmap)
                    4. Text processing (e.g., sed, awk, cut, tr, sort, uniq)
                    5. Package management (apt, yum, dnf, pacman, snap, flatpak)
                    6. Process management (ps, top, htop, kill, nice, renice)
                    7. Disk management (fdisk, parted, lvm, mount, umount, df, du)
                    8. User and permission management (chmod, chown, sudo, su)
                    9. Shell scripting (bash, zsh, fish)
                    10. Version control systems (git, svn)
                    11. Container and virtualization tools (docker, podman, kubectl, virsh)
                    12. Cloud provider CLIs (aws, gcloud, azure)
                    13. Performance monitoring and tuning (iostat, vmstat, sar, perf)
                    14. Security tools (iptables, ufw, selinux, apparmor)
                    15. Remote access and file transfer (ssh, scp, rsync, sftp)
                    16. Performance testing and network benchmarking tools (speedtest-cli, iperf3)

                    Guidelines for providing commands:

                    1. Analyze the user's query thoroughly to understand the intended operation and context.
                    2. Provide the most efficient and appropriate command(s) for the task.
                    3. Handle potential edge cases and provide safeguards against data loss or system damage.
                    4. Include necessary options and arguments, explaining their purpose when not obvious.
                    5. For complex operations, provide both a basic version and an advanced version with additional features.
                    6. When applicable, suggest alternative commands or tools that might better suit the task.
                    7. For destructive operations, include appropriate warnings and suggest using '--dry-run' options when available.
                    8. Handle common system directories by using '~/' for the user's home directory.
                    9. For commands that might vary across distributions, provide variants for major distros (e.g., Debian/Ubuntu, RHEL/CentOS, Arch).
                    10. If a single command is insufficient, provide a short script or one-liner that combines multiple commands.
                    11. For operations that might require elevated privileges, include 'sudo' where appropriate.
                    12. Provide guidance on how to replace placeholders for environment-specific information.
                    13. Ensure all backslashes in commands are properly escaped in the JSON response.
                    14. If the exact location of a file is unknown, provide commands to search for it in common directories.
                    15. For file operations, always include safeguards against accidental overwrites or deletions.
                    16. For tools that might not be installed by default, include commands to install them using common package managers.
                    17. When suggesting network tools, consider both installed packages and downloadable scripts (e.g., speedtest-cli).

                    Respond with a JSON object containing an array of command objects. Each command object should have a 'command' field with the full command string, a 'description' field explaining the command's purpose and any relevant details, and an 'installation' field with the command to install any required tools if they're not typically pre-installed. Include at least one command, but provide alternatives when applicable. Do not include any text outside of the JSON object.

                Example response format:

                {
                    "commands": [
                        {
                            "command": "speedtest-cli",
                            "description": "Runs a speed test using the official speedtest.net cli tool.",
                            "installation": "sudo apt-get install speedtest-cli  # For Debian/Ubuntu"
                        },
                        {
                            "command": "curl -s https://raw.githubusercontent.com/sivel/speedtest-cli/master/speedtest.py | python -",
                            "description": "Downloads and runs the speedtest-cli Python script directly without installation.",
                            "installation": "sudo apt-get install curl python  # For Debian/Ubuntu"
                        },
                        {
                            "command": "iperf3 -c iperf3.speedtest.net",
                            "description": "Runs a network speed test using iperf3 to a public iperf3 server.",
                            "installation": "sudo apt-get install iperf3  # For Debian/Ubuntu"
                        }
                    ]
                }
                """
            },
            {
                "role": "user",
                "content": query
            }
        ],
        temperature=0.2,
        max_tokens=1000,
        top_p=1,
        stream=False,
        stop=None
    )

    try:
        # First, try to parse the response as-is
        data = json.loads(completion.choices[0].message.content.strip())
    except json.JSONDecodeError:
        # If parsing fails, attempt to fix common issues
        content = completion.choices[0].message.content.strip()

        # Replace unescaped backslashes with escaped ones
        content = re.sub(r'(?<!\\)\\(?![\\"{}])', r'\\\\', content)

        # Remove any text outside of the JSON object
        content = re.search(r'\{.*\}', content, re.DOTALL)
        if content:
            content = content.group(0)
        else:
            raise ValueError("No valid JSON object found in the response")

        # Try parsing the cleaned content
        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            print("Raw content:")
            print(content)
            raise ValueError("Failed to parse the response as JSON")

    # Validate the structure of the parsed data
    if not isinstance(data, dict) or 'commands' not in data or not isinstance(data['commands'], list):
        raise ValueError("Invalid response structure")

    for cmd in data['commands']:
        if not isinstance(cmd, dict) or 'command' not in cmd:
            raise ValueError("Invalid command structure in response")

    return data

def handle_error(error_message):
    completion = client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": """
                You are an expert Linux troubleshooter, specialized in diagnosing and resolving command-line errors. Your task is to analyze the error message provided, identify the root cause, and suggest appropriate solutions. Your expertise covers:

                1. Command not found errors
                2. Permission issues
                3. Syntax errors in commands
                4. Missing dependencies or libraries
                5. Network-related issues
                6. File system errors
                7. Resource constraints (CPU, memory, disk space)
                8. Configuration problems
                9. Version incompatibilities
                10. OS-specific quirks across different Linux distributions

                Guidelines for providing solutions:

                1. Carefully analyze the error message to identify the specific issue.
                2. Provide a clear explanation of the problem in simple terms.
                3. Suggest the most likely solution as the primary recommendation.
                4. If applicable, provide alternative solutions or workarounds.
                5. Include commands to implement the solutions, with explanations.
                6. Consider the context of the original command that caused the error.
                7. If the solution involves installing software, provide commands for major Linux distributions (e.g., Debian/Ubuntu, RHEL/CentOS, Arch).
                8. Warn about any potential risks associated with the suggested solutions.
                9. If the error message is ambiguous, provide solutions for the most likely scenarios.
                10. For complex issues, suggest diagnostic steps to gather more information.

                Respond with a JSON object containing an 'explanation' field describing the issue, and a 'solutions' array with objects containing 'description' and 'command' fields for each suggested solution. Provide at least one solution, but include alternatives when applicable. Do not include any text outside of the JSON object.

                Example response format:

                {
                    "explanation": "The 'speedtest-cli' command is not installed on your system.",
                    "solutions": [
                        {
                            "description": "Install speedtest-cli using apt (for Debian/Ubuntu)",
                            "command": "sudo apt-get update && sudo apt-get install speedtest-cli"
                        },
                        {
                            "description": "Install speedtest-cli using pip (Python package manager)",
                            "command": "pip install speedtest-cli"
                        },
                        {
                            "description": "Run speedtest-cli directly without installation using Python",
                            "command": "curl -s https://raw.githubusercontent.com/sivel/speedtest-cli/master/speedtest.py | python -"
                        }
                    ]
                }
                """
            },
            {
                "role": "user",
                "content": f"Error message: {error_message}"
            }
        ],
        temperature=0.2,
        max_tokens=1000,
        top_p=1,
        stream=False,
        stop=None
    )

    try:
        data = json.loads(completion.choices[0].message.content.strip())
    except json.JSONDecodeError:
        raise ValueError("Failed to parse the error handling response as JSON")

    if not isinstance(data, dict) or 'explanation' not in data or 'solutions' not in data:
        raise ValueError("Invalid error handling response structure")

    return data

def get_key():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def display_and_select_command(commands):
    selected = 0
    while True:
        print("\033[2J\033[H", end="")  # Clear screen
        print("Welcome to groq-cli. Use arrows to select or press 'c' to cancel")
        for idx, cmd in enumerate(commands):
            if idx == selected:
                print(f"\033[1;32m» {cmd['command']}\033[0m")
                print(f"  \033[1;32m{cmd['description']}\033[0m")
            else:
                print(f"  {cmd['command']}")

        key = get_key()
        if key == '\x1b':
            key = get_key()
            if key == '[':
                key = get_key()
                if key == 'A':  # Up arrow
                    selected = (selected - 1) % len(commands)
                elif key == 'B':  # Down arrow
                    selected = (selected + 1) % len(commands)
        elif key == 'c':  # Cancel
            return None
        elif key == '\r':  # Enter key
            return commands[selected]

def display_and_select_solution(solutions):
    selected = 0
    while True:
        print("\033[2J\033[H", end="")  # Clear screen
        print("Use arrows to select a solution or press 'c' to cancel")
        for idx, solution in enumerate(solutions):
            if idx == selected:
                print(f"\033[1;32m» {solution['command']}\033[0m")
                print(f"  \033[1;32m{solution['description']}\033[0m")
            else:
                print(f"  {solution['command']}")

        key = get_key()
        if key == '\x1b':
            key = get_key()
            if key == '[':
                key = get_key()
                if key == 'A':  # Up arrow
                    selected = (selected - 1) % len(solutions)
                elif key == 'B':  # Down arrow
                    selected = (selected + 1) % len(solutions)
        elif key == 'c':  # Cancel
            return None
        elif key == '\r':  # Enter key
            return solutions[selected]

def execute_command(command):
    print(f"\nExecuting: {command}")
    try:
        # Use bash to execute the command, which allows for proper expansion of {1..10}
        result = subprocess.run(['bash', '-c', command], check=True, text=True, capture_output=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        print(f"Exit code: {e.returncode}")
        if e.stdout:
            print("Standard output:")
            print(e.stdout)
        if e.stderr:
            print("Standard error:")
            print(e.stderr)

        # Handle the error
        error_data = handle_error(str(e))
        print("\nError Analysis:")
        print(error_data['explanation'])
        print("\nSuggested Solutions:")
        for idx, solution in enumerate(error_data['solutions'], 1):
            print(f"{idx}. {solution['description']}")

        # Allow the user to select and execute a solution using arrow keys
        selected_solution = display_and_select_solution(error_data['solutions'])
        if selected_solution:
            execute_command(selected_solution['command'])
        else:
            print("No solution selected. Command execution cancelled.")
    except FileNotFoundError:
        print(f"Error: Command '{command.split()[0]}' not found. Please check if it's installed and in your PATH.")
        print("Command execution cancelled.")
    except PermissionError:
        print(f"Error: Permission denied when trying to execute '{command.split()[0]}'.")
        print("Command execution cancelled.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        print("Command execution cancelled.")
    return False

def main():
    parser = argparse.ArgumentParser(description="CLI tool for generating commands using Groq.")
    parser.add_argument("query", nargs="+", help="The operation you want to perform")
    args = parser.parse_args()

    query = " ".join(args.query)
    result = get_commands(query)

    if result is None:
        print("Failed to get valid commands. Please try again.")
        return

    selected_command = display_and_select_command(result['commands'])

    if selected_command:
        success = execute_command(selected_command['command'])
        if not success and 'installation' in selected_command:
            print(f"\nNote: If the command is not found, you may need to install it using:")
            print(selected_command['installation'])
    else:
        print("No command selected.")

if __name__ == "__main__":
    main()
