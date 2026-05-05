# Tarea 05 — Agentic Loop y stop_reason

## 📋 Descripción

Implementación de un agente inteligente que **clasifica leads de Calendly** usando un agentic loop robusto. La tarea se enfoca en evitar los 3 anti-patterns más comunes al construir bucles de agentes.

**Status:** ✅ COMPLETADA

---

## 🎯 Objetivo de la Tarea

Aprender a construir un agentic loop que:
- Ejecute múltiples iteraciones de forma controlada
- Use `stop_reason` como señal confiable (no parsing de texto)
- Implemente herramientas estructuradas que terminen el loop
- Maneje correctamente `max_iterations` como fallback de seguridad

---

## 📊 Entrada y Salida

### Entrada
```
Nombre: [string del prospect]
Budget: [número en USD o "ninguno"]
```

### Salida
```
{
  "nombre": "...",
  "budget": [...],
  "prioridad": "ALTA | MEDIA | BAJA | REQUIERE_INFO"
}
```

---

## 🔍 Flujo del Agente

```
┌─────────────────────────────────────┐
│ INPUT: nombre, budget               │
└──────────────────┬──────────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │ Iteración 1          │
        │ stop_reason=tool_use │
        │ → buscar_info()      │
        └──────────────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │ Iteración 2          │
        │ stop_reason=tool_use │
        │ → clasificar_lead()  │
        └──────────────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │ stop_reason=end_turn │
        │ → RETURN OUTPUT      │
        └──────────────────────┘
```

---

## 📏 Reglas de Clasificación

| Budget | Prioridad |
|--------|-----------|
| > $50,000 | **ALTA** |
| $20,000 - $50,000 | **MEDIA** |
| < $20,000 | **BAJA** |
| $0 o None | **REQUIERE_INFO** |

---

## ⚠️ Anti-patterns Evitados

### ❌ Anti-pattern #1: Parsear Texto
**El problema:**
```python
if "ALTA" in response.content[0].text:
    prioridad = "ALTA"
```
Frágil, depende de exactitud del modelo.

**La solución:**
Las herramientas retornan JSON estructurado:
```json
{
  "prioridad": "ALTA"
}
```
El modelo no elige cómo comunicarse, usa la estructura de la herramienta.

---

### ❌ Anti-pattern #2: `max_iterations` como Control Principal
**El problema:**
```python
# Creer que max_iterations=5 garantiza clasificación
for i in range(5):
    response = client.messages.create(...)
    if "FIN" in response.text:
        break
```

**La solución:**
- `max_iterations` es un **fallback de seguridad**, no control
- El control real está en **qué herramientas usa el modelo**
- El agente debe tener una herramienta explícita que indique "terminé": `clasificar_lead()`

```python
# Correcto: confiar en que el modelo usará clasificar_lead()
while True:
    response = client.messages.create(...)
    if response.stop_reason == "end_turn":
        break
    # procesar tool_use...
```

---

### ❌ Anti-pattern #3: Señales Textuales
**El problema:**
```python
# Esperar que el modelo diga "FIN" o "TERMINADO"
if "TERMINADO" in response.text:
    break
```
Depende del idioma, formato, caprichos del modelo.

**La solución:**
Confiar en `stop_reason`:
```python
if response.stop_reason == "end_turn":
    # El agente terminó naturalmente
    break
elif response.stop_reason == "tool_use":
    # Procesar tool_use y continuar
    continue
```

---

## 🚀 Ejecución

### Requisitos Previos
```bash
# API Key configurada en .env
ANTHROPIC_API_KEY=sk-ant-...
CLAUDE_MODEL=claude-haiku-4-5-20251001
```

### Ejecución Básica
```powershell
cd D:\KREANTE\z__learning\Kreante\mayo-4\tarea-05
python agent.py
```

### Ejemplos de Ejecución

#### Ejemplo 1: Clasificación Normal
```powershell
python agent.py
Nombre: Juan García
Budget: 50000
→ Prioridad: MEDIA
```

#### Ejemplo 2: Presupuesto Alto
```powershell
python agent.py
Nombre: María López
Budget: 75000
→ Prioridad: ALTA
```

#### Ejemplo 3: Sin Presupuesto
```powershell
python agent.py
Nombre: Carlos
Budget: ninguno
→ Prioridad: REQUIERE_INFO
```

#### Ejemplo 4: Simulación de max_iterations
```powershell
python -c "from agent import clasificar; print(clasificar('Juan', 50000, max_iterations=1))"
→ {'prioridad': 'max_iterations'}
```

---

## 📚 Conceptos Clave Aprendidos

### 1. **stop_reason es el Signal Confiable**
```python
if response.stop_reason == "tool_use":
    # El modelo quiere usar una herramienta
elif response.stop_reason == "end_turn":
    # El modelo terminó naturalmente
```

### 2. **Herramientas Estructuradas Evitan Ambigüedad**
La estructura de `tools` define exactamente qué parámetros retorna cada herramienta:
```python
{
    "name": "clasificar_lead",
    "input_schema": {
        "properties": {
            "prioridad": {"enum": ["ALTA", "MEDIA", "BAJA", "REQUIERE_INFO"]}
        }
    }
}
```

### 3. **max_iterations es Fallback, No Control**
- `max_iterations` previene loops infinitos (seguridad)
- El verdadero control está en qué herramientas usa el modelo
- Si llega a `max_iterations` sin usar `clasificar_lead()` → retorna `"max_iterations"`

### 4. **El Agente Necesita Herramienta Explícita de Término**
```python
# El agente debe tener una herramienta que indique "ya terminé"
tools = [
    {"name": "buscar_info", ...},
    {"name": "clasificar_lead", ...}  # ← Esta cierra el loop
]
```

---

## 📁 Archivos Incluidos

| Archivo | Descripción |
|---------|-------------|
| `agent.py` | Implementación completa del agente clasificador |
| `CLAUDE.md` | Contexto técnico y preguntas guía |
| `README.md` | Este archivo — guía de uso |
| `logs/` | Logs de validación y ejemplos de ejecución |

---

## 🧪 Validación

El agente debe cumplir con:
- ✅ Ejecutar exactamente 2 iteraciones en casos normales
- ✅ Usar `stop_reason` para controlar el flujo (no texto)
- ✅ Retornar JSON estructurado con `prioridad`
- ✅ Respetar `max_iterations` como fallback
- ✅ Clasificar correctamente según reglas de presupuesto

---

## 💡 Ejercicios Relacionados

- **Tarea 06:** Hooks vs Prompts — Agente generador de devis con bloqueos via PreToolUse
- **Tarea 07:** Hub-and-spoke — Coordinador de briefs con 3 subagentes en paralelo

---

## 📞 Soporte

Para preguntas sobre la implementación, consulta:
1. `CLAUDE.md` en esta carpeta (contexto técnico)
2. `agent.py` (código comentado)
3. El hub principal: `../CLAUDE.md`
