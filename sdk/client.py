from anthropic import Anthropic
import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

def get_client():
    """Inicializa y retorna cliente de Anthropic con API key desde .env."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY no configurada en .env")
    return Anthropic(api_key=api_key)

client = get_client()
MODEL = os.getenv("CLAUDE_MODEL", "claude-haiku-4-5-20251001")
