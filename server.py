#!/usr/bin/env python3
import asyncio
import json
import sys
import subprocess
from typing import Any, Dict, List, Optional
from mcp.server import Server
from mcp.types import Tool, TextContent
import mcp.server.stdio

app = Server("whisper-cli-mcp")

@app.list_tools()
async def list_tools() -> List[Tool]:
    return [
        Tool(
            name="whisper_transcribe",
            description="Transcribe audio files using whisper-cli",
            inputSchema={
                "type": "object",
                "properties": {
                    "audio_file": {
                        "type": "string",
                        "description": "Path to the audio file to transcribe"
                    },
                    "model": {
                        "type": "string",
                        "description": "Whisper model to use (base, small, medium, large, large-v2, large-v3)",
                        "default": "base"
                    },
                    "language": {
                        "type": "string",
                        "description": "Language code for transcription (optional, auto-detect if not provided)"
                    },
                    "output_format": {
                        "type": "string",
                        "description": "Output format (txt, vtt, srt, json)",
                        "default": "txt"
                    }
                },
                "required": ["audio_file"]
            }
        ),
        Tool(
            name="shell_command",
            description="Execute shell commands safely",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Shell command to execute"
                    },
                    "working_directory": {
                        "type": "string",
                        "description": "Working directory for the command (optional)"
                    }
                },
                "required": ["command"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    if name == "whisper_transcribe":
        return await transcribe_audio(arguments)
    elif name == "shell_command":
        return await execute_shell_command(arguments)
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]

async def transcribe_audio(args: Dict[str, Any]) -> List[TextContent]:
    audio_file = args["audio_file"]
    model = args.get("model", "base")
    language = args.get("language")
    output_format = args.get("output_format", "txt")

    # Build whisper command
    cmd = ["whisper-cli", audio_file, "--model", model, "--output_format", output_format]

    if language:
        cmd.extend(["--language", language])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        if result.returncode == 0:
            return [TextContent(
                type="text",
                text=f"Transcription successful!\n\nStdout:\n{result.stdout}\n\nStderr:\n{result.stderr}"
            )]
        else:
            return [TextContent(
                type="text",
                text=f"Transcription failed with exit code {result.returncode}\n\nStderr:\n{result.stderr}"
            )]
    except subprocess.TimeoutExpired:
        return [TextContent(type="text", text="Transcription timed out after 5 minutes")]
    except FileNotFoundError:
        return [TextContent(type="text", text="whisper command not found. Please install OpenAI Whisper.")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error during transcription: {str(e)}")]

async def execute_shell_command(args: Dict[str, Any]) -> List[TextContent]:
    command = args["command"]
    working_directory = args.get("working_directory")

    # Security: Basic command validation
    dangerous_commands = ["rm -rf", "sudo", "chmod 777", "dd if=", "> /dev/"]
    if any(dangerous in command for dangerous in dangerous_commands):
        return [TextContent(type="text", text="Command contains potentially dangerous operations and was blocked.")]

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=working_directory
        )

        output = f"Exit code: {result.returncode}\n\n"
        if result.stdout:
            output += f"Stdout:\n{result.stdout}\n\n"
        if result.stderr:
            output += f"Stderr:\n{result.stderr}"

        return [TextContent(type="text", text=output)]

    except subprocess.TimeoutExpired:
        return [TextContent(type="text", text="Command timed out after 30 seconds")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error executing command: {str(e)}")]

async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
