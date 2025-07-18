# Whisper CLI MCP Server

An MCP server that provides shell command execution and OpenAI Whisper transcription capabilities.

## Features

- **whisper_transcribe**: Transcribe audio files using OpenAI Whisper
- **shell_command**: Execute shell commands safely with basic security validation

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Make the server executable:
```bash
chmod +x server.py
```

## Usage

### Running the Server

```bash
python server.py
```

### Tools Available

#### whisper_transcribe
Transcribe audio files using whisper-cli.

Parameters:
- `audio_file` (required): Path to the audio file
- `model` (optional): Whisper model (base, small, medium, large, large-v2, large-v3)
- `language` (optional): Language code for transcription
- `output_format` (optional): Output format (txt, vtt, srt, json)

#### shell_command
Execute shell commands with basic security validation.

Parameters:
- `command` (required): Shell command to execute
- `working_directory` (optional): Working directory for the command

## Security

The shell_command tool includes basic security validation to prevent execution of potentially dangerous commands. Commands containing the following patterns are blocked:
- `rm -rf`
- `sudo`
- `chmod 777`
- `dd if=`
- `> /dev/`

## Configuration

To use this server with Claude Desktop, add the following to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "whisper-cli-mcp": {
      "command": "python",
      "args": ["/path/to/whisper-cli-mcp/server.py"]
    }
  }
}
```