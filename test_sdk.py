#!/usr/bin/env python3
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

if not os.getenv("ANTHROPIC_API_KEY"):
    print("ERROR: ANTHROPIC_API_KEY no configurada en .env")
    sys.exit(1)

from sdk import client, MODEL

response = client.messages.create(
    model=MODEL,
    max_tokens=50,
    messages=[{"role": "user", "content": "OK"}]
)

print(f"[OK] SDK funciona. Respuesta: {response.content[0].text.strip()}")
