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

## Setup
- SDK: `anthropic` (Anthropic SDK para Python)
- API Key: variable de entorno `ANTHROPIC_API_KEY`
- **Cliente centralizado:** todas las tareas importan desde `sdk.client`

### Desde cualquier tarea:
```python
from sdk import client, MODEL

response = client.messages.create(
    model=MODEL,
    max_tokens=1024,
    messages=[...]
)
```

**Configuración (archivo `.env`):**
```env
ANTHROPIC_API_KEY=tu-api-key-aqui
CLAUDE_MODEL=claude-haiku-4-5-20251001
```
- API key configurada ✓
- Modelo: Haiku 4.5 (configurable)

- Cada tarea incluye `README.md` con instrucciones y logs de validación

## Setup Completado ✓
- ✅ Carpetas de tareas (tarea-05, tarea-06, tarea-07) creadas
- ✅ CLAUDE.md específico en cada tarea con preguntas guía
- ✅ SDK centralizado (`sdk/client.py`) con cliente Anthropic
- ✅ `.env` configurado con API key y modelo (claude-haiku-4-5-20251001)
- ✅ `test_sdk.py` validado y funcionando
- ✅ `.gitignore` protege `.env` de commits

## Convenciones
- Respuestas concisas
- Herramientas dedicadas (Read, Edit, Glob, Grep) en lugar de Bash
- Cada tarea tiene su propio `CLAUDE.md` con contexto específico
- Documentación en español
- **Lenguaje:** Python únicamente
- **Versionado:** Git (commits regulares)
- **SDK:** Claude API (Anthropic SDK) - Haiku 4.5
- **Configuración:** API key en `.env`
- **Documentación:** `README.md` + logs de validación en cada tarea
