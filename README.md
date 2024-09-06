# groq-cli

groq-cli is a command-line interface tool that leverages the Groq API to generate and execute Linux commands based on user queries. It provides an interactive way to find and run the most appropriate commands for various Linux operations.

## Features

- Generate Linux commands based on natural language queries
- Interactive command selection using arrow keys
- Automatic command execution
- Error handling and solution suggestions
- Support for a wide range of Linux operations and tools

## Prerequisites

- Python 3.6+
- Groq API key

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/Balogunolalere/groq-cli.git
   cd groq-cli
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up your Groq API key:
   Create a `.env` file in the project root and add your Groq API key:
   ```
   GROQ_API_KEY=your_api_key_here
   ```

## Usage

Run the script with your query as arguments:

```
python groq_cli.py "your query here"
```

For example:
```
python groq_cli.py how to check disk space
```

Use arrow keys to select a command, press Enter to execute, or 'c' to cancel.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.


## Acknowledgments

- Groq for providing the API
- All contributors to the project