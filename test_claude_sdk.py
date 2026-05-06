import asyncio
from sdk.client_claude_sdk import (
    query,
    ClaudeAgentOptions,
    MODEL,
    AssistantMessage,
    ResultMessage,
    TextBlock,
)


async def main():
    print(f"Probando claude-agent-sdk — modelo: {MODEL}")
    print("-" * 40)

    options = ClaudeAgentOptions(model=MODEL)

    async for message in query(
        prompt="Responde en una sola oración: ¿cuál es la capital de Francia?",
        options=options,
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"Respuesta: {block.text}")
        elif isinstance(message, ResultMessage):
            print(f"\nConexión OK")
            print(f"Turnos    : {message.num_turns}")
            print(f"Costo     : ${message.total_cost_usd:.6f}")


if __name__ == "__main__":
    asyncio.run(main())
