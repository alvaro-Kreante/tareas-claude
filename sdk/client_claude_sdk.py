from claude_agent_sdk import (
    query,
    ClaudeSDKClient,
    ClaudeAgentOptions,
    AgentDefinition,
    AssistantMessage,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
    ToolResultBlock,
)
import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Aliases válidos: "haiku", "sonnet", "opus" (distinto al anthropic SDK que usa IDs completos)
MODEL = os.getenv("CLAUDE_AGENT_MODEL", "haiku")

__all__ = [
    "query",
    "ClaudeSDKClient",
    "ClaudeAgentOptions",
    "AgentDefinition",
    "AssistantMessage",
    "ResultMessage",
    "TextBlock",
    "ToolUseBlock",
    "ToolResultBlock",
    "MODEL",
]
