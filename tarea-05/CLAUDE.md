# Tarea 05 — Agentic Loop y stop_reason

## Objetivo
Implementar un agente que clasifica leads de Calendly identificando los 3 anti-patterns clásicos del agentic loop.

## Contexto
Un agente que recibe leads de Calendly y debe clasificarlos en categorías de prioridad. El agente tiene acceso a una herramienta para buscar información del prospect en una base de datos.

## Anti-patterns a Identificar
1. **Parsear texto de respuestas del modelo** — Confiar en parse manual de `content[0].text` para lógica crítica
2. **Usar `max_iterations` como stop condition** — Creer que limitar iteraciones es suficiente para garantizar salida
3. **Usar contenido textual como signal determinístico** — Confiar en que el modelo siempre diga "FIN" o similar

## Preguntas Guía
1. ¿Cuál es la diferencia entre `stop_reason="tool_use"` vs `stop_reason="end_turn"`?
2. ¿Qué sucede si el modelo no sigue exactamente el formato que esperas en la respuesta?
3. ¿Por qué `max_iterations` solo limita intentos pero no garantiza que el agente termine correctamente?
4. ¿Cómo debería el agente **conocer** que debe dejar de iterar?

## Estructura Esperada
```
tarea-05/
├── CLAUDE.md (este archivo)
├── README.md (instrucciones y ejecución)
├── agent.py (implementación del agente)
└── logs/ (validaciones y traces)
```

## Notas
- Python únicamente
- Usa el SDK de Anthropic (cliente `anthropic`)
- API key en variable de entorno `ANTHROPIC_API_KEY`
- Incluye logs detallados de cada iteración del loop
- Documenta el `stop_reason` de cada respuesta
