# Tarea 05 — Agentic Loop y stop_reason

## Status: COMPLETADA ✓

## Objetivo
Implementar un agente que clasifica leads de Calendly identificando y evitando los 3 anti-patterns clásicos del agentic loop.

## Implementación

### Entrada
- **Nombre**: string del prospect
- **Budget**: número o "ninguno"

### Salida
- **Prioridad**: ALTA, MEDIA, BAJA, o REQUIERE_INFO

### Flujo del Agente
1. **Iteración 1**: `stop_reason=tool_use` → usa `buscar_info` (nombre, budget)
2. **Iteración 2**: `stop_reason=tool_use` → usa `clasificar_lead` (termina)

### Reglas de Clasificación
- Budget > 50000 → **ALTA**
- Budget 20000-50000 → **MEDIA**
- Budget < 20000 → **BAJA**
- Budget = 0 o None → **REQUIERE_INFO**

### Anti-patterns Evitados

#### ❌ Anti-pattern #1: Parsear texto
**Lo malo:** Confiar en `if "ALTA" in response.content[0].text`
**La solución:** Las herramientas retornan JSON estructurado con parámetro `prioridad`

#### ❌ Anti-pattern #2: `max_iterations` como control principal
**Lo malo:** Creer que `max_iterations=5` garantiza que el agente clasifique
**La solución:** El control está en **usar la herramienta `clasificar_lead`**, no en iteraciones
- Si llega a `max_iterations` sin clasificar → retorna `"max_iterations"`
- `max_iterations` es solo un fallback de seguridad

#### ❌ Anti-pattern #3: Señales textuales
**Lo malo:** Esperar que el modelo diga "FIN" o "TERMINADO"
**La solución:** Confiar en `stop_reason` y herramientas estructuradas
- `stop_reason="tool_use"` → continúa
- `stop_reason="end_turn"` → terminó

## Ejecución

```powershell
cd D:\KREANTE\z__learning\Kreante\mayo-4\tarea-05
python agent.py
```

### Ejemplo Normal
```
Nombre: Juan
Budget: 50000
→ Prioridad: MEDIA
```

### Ejemplo con max_iterations
```powershell
python -c "from agent import clasificar; print(clasificar('Juan', 50000, max_iterations=1)['prioridad'])"
→ Prioridad: max_iterations
```

## Conceptos Clave Aprendidos
1. **stop_reason es el signal confiable**, no el parsing de texto
2. **Herramientas estructuradas** evitan ambigüedad
3. **max_iterations es fallback, no control** — el verdadero control está en qué herramientas usa el modelo
4. El agente debe tener una herramienta explícita que indique "terminé" (clasificar_lead)

## Archivos
- `agent.py` — Implementación completa del loop agentico
- `CLAUDE.md` — Este archivo (contexto de la tarea)
