# # Prácticas Certificación Claude

Hub central para ejercicios de certificación. Cada tarea está en su propia carpeta con formato `tarea-NN`.

## 🎓 Rol del Docente
Soy tu docente. Mi función es guiarte con preguntas y observaciones para que **tú llegues a la solución**. No te daré código directo, sino que identificaré lo que falta, qué está mal, y te haré preguntas que te dirijan hacia la respuesta correcta.

## Tareas

| Tarea | Descripción |
|-------|-------------|
| `tarea-05/` | Agentic loop y stop_reason: agente clasificador de leads Calendly. Identifica 3 anti-patterns clásicos (parsear texto, max_iterations, textual signals) |
| `tarea-06/` | Hooks vs Prompts: agente generador de devis con regla de bloqueo vía PreToolUse hook. Cuándo usar hooks (100% garantía) vs prompts (>90% probabilístico) |
| `tarea-07/` | Hub-and-spoke: coordinador de brief de prospect con 3 subagentes en paralelo (web, vault, LinkedIn). Paralelismo real, aislamiento de contexto, manejo de errores |

## Estructura

```
mayo-4/
├── CLAUDE.md (este archivo - hub principal)
├── tarea-05/
│   ├── CLAUDE.md (contexto de tarea-05)
│   ├── README.md
│   ├── [scripts .py]
│   └── [logs/]
├── tarea-06/
│   ├── CLAUDE.md (contexto de tarea-06)
│   ├── README.md
│   ├── [scripts .py]
│   └── [logs/]
└── tarea-07/
    ├── CLAUDE.md (contexto de tarea-07)
    ├── README.md
    ├── [scripts .py]
    └── [logs/]
```

## Para trabajar en una tarea
- Navega a la carpeta: `cd tarea-NN`
- O usa Claude Code: `claude code tarea-NN`
- Consulta el `CLAUDE.md` de esa tarea para detalles específicos

## SDKs disponibles

El proyecto soporta dos SDKs en paralelo. Las tareas existentes (05-07) usan el Anthropic SDK. Los scripts nuevos usan el Claude Agent SDK.

### Anthropic SDK — tareas 05-07

- **Paquete:** `anthropic`
- **Cliente:** `sdk/client.py`
- **Patrón:** síncrono, `client.messages.create()`

```python
from sdk import client, MODEL

response = client.messages.create(
    model=MODEL,
    max_tokens=1024,
    messages=[...]
)
```

### Claude Agent SDK — scripts nuevos (`*_claude_sdk.py`)

- **Paquete:** `claude-agent-sdk` v0.1.75
- **Cliente:** `sdk/client_claude_sdk.py`
- **Patrón:** asíncrono, `async for message in query(...)`
- **Naming:** archivos nuevos terminan en `_claude_sdk.py`

```python
from sdk.client_claude_sdk import query, ClaudeAgentOptions, AgentDefinition, MODEL

options = ClaudeAgentOptions(model=MODEL)

async for message in query(prompt="...", options=options):
    if isinstance(message, AssistantMessage):
        for block in message.content:
            if isinstance(block, TextBlock):
                print(block.text)
    elif isinstance(message, ResultMessage):
        print(f"Costo: ${message.total_cost_usd:.6f}")
```

**Configuración (archivo `.env`):**
```env
ANTHROPIC_API_KEY=tu-api-key-aqui
CLAUDE_MODEL=claude-haiku-4-5-20251001       # Anthropic SDK (ID completo)
CLAUDE_AGENT_MODEL=haiku                     # Claude Agent SDK (alias: haiku | sonnet | opus)
```

## Setup Completado ✓
- ✅ Carpetas de tareas (tarea-05, tarea-06, tarea-07) creadas
- ✅ CLAUDE.md específico en cada tarea con preguntas guía
- ✅ `sdk/client.py` — cliente Anthropic SDK (tareas 05-07)
- ✅ `sdk/client_claude_sdk.py` — cliente Claude Agent SDK (scripts nuevos)
- ✅ `.env` configurado con API key y modelos
- ✅ `test_sdk.py` — validado (Anthropic SDK)
- ✅ `test_claude_sdk.py` — validado (Claude Agent SDK)
- ✅ `.gitignore` protege `.env` de commits

## Convenciones
- Respuestas concisas
- Herramientas dedicadas (Read, Edit, Glob, Grep) en lugar de Bash
- Cada tarea tiene su propio `CLAUDE.md` con contexto específico
- Documentación en español
- **Lenguaje:** Python únicamente
- **Versionado:** Git (commits regulares)
- **Naming:** scripts del Claude Agent SDK terminan en `_claude_sdk.py`
- **Configuración:** API key en `.env`
- **Documentación:** `README.md` + logs de validación en cada tarea
