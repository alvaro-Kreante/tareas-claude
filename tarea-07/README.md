# Tarea 07 — Hub-and-Spoke con Subagentes en Paralelo

## Objetivo
Implementar un **coordinador** que investiga prospects mediante **3 subagentes independientes** que operan en paralelo. Practica:
- Paralelismo real en respuestas de agentes
- Aislamiento de contexto entre subagentes
- Manejo de errores distribuido
- Agregación de resultados

---

## 🏗️ Arquitectura

```
coordinator.py (agente hub)
    ├─ run_web_agent() → subagent_web.py
    ├─ run_vault_agent() → subagent_vault.py
    └─ run_contact_agent() → subagent_contact.py
```

### Flujo de Ejecución

1. **Usuario input** → nombre de prospect
2. **Coordinador pregunta** → qué fuentes (web, vault, contact, todas)
3. **Coordinador arma prompt** → dinámico basado en selección
4. **Coordinador delega** → 3 subagentes se lanzan en paralelo
5. **Subagentes retornan** → `{status, data, citations}`
6. **Coordinador agrega** → JSON final estructurado
7. **Output** → print en pantalla

---

## 📁 Archivos

| Archivo | Rol |
|---------|-----|
| `coordinator.py` | Agente hub: orquesta investigación |
| `subagent_web.py` | Subagente 1: búsqueda web/LinkedIn |
| `subagent_vault.py` | Subagente 2: historial interno |
| `subagent_contact.py` | Subagente 3: datos de contacto |

---

## 🚀 Cómo Ejecutar

### Requisitos
```bash
python >= 3.10
SDK Anthropic configurado (ver CLAUDE.md del proyecto)
.env con ANTHROPIC_API_KEY
```

### Ejecución Principal
```bash
cd tarea-07
python coordinator.py
```

### Entrada del Usuario
```
¿Nombre del prospect a investigar? Juan García
¿Qué fuentes deseas consultar?
  1) Web/LinkedIn
  2) Vault (historial interno)
  3) Datos de contacto
  4) Todas las fuentes

Opción (1-4): 4
```

### Output Esperado
```json
{
  "prospect_name": "Juan García",
  "investigation": {
    "web": {
      "status": "found",
      "data": {
        "full_name": "Juan García Pérez",
        "title": "Senior Product Manager",
        "company": "TechCorp Spain",
        "location": "Madrid, España",
        "summary": "..."
      },
      "citations": [
        {"host": "linkedin.com", "url": "https://linkedin.com/..."}
      ]
    },
    "vault": {
      "status": "found",
      "data": {
        "last_interaction": "2024-03-15",
        "total_interactions": 3,
        "lead_status": "warm"
      },
      "citations": []
    },
    "contact": {
      "status": "found",
      "data": {
        "email": "juan.garcia@techcorp.com",
        "phone": "+34 91 123 4567",
        "preferred_contact": "email"
      },
      "citations": []
    }
  },
  "all_citations": [...]
}
```

---

## 🎓 Teoría & Decisiones Clave

### 1. Paralelismo en Claude API

**¿Cómo se lanzan 3 subagentes en paralelo?**

En el agentic loop, el coordinador emite instrucciones como:
> "Delega búsquedas a web_search, vault_search y contact_search"

Claude retorna **3 Tool calls en una respuesta**:
```python
response.content = [
    ToolUseBlock(name="web_search", id="1", input={...}),
    ToolUseBlock(name="vault_search", id="2", input={...}),
    ToolUseBlock(name="contact_search", id="3", input={...})
]
```

Python procesa todos juntos. **La API de Claude los ejecuta en paralelo** (no es responsabilidad de Python).

---

### 2. Contexto Aislado

**Cada subagente NO ve el contexto de los otros:**

- **Web agent**: solo nombre + max_iterations. No ve vault, no ve contactos previos.
- **Vault agent**: solo nombre + max_iterations. No ve web research. Accede solo a BD interna.
- **Contact agent**: solo nombre + max_iterations. No ve historial completo.

**Implementación**: Cada subagente recibe un prompt minimalista y tools específicas para su dominio.

```python
def run_web_agent(prospect_name: str, max_iterations: int):
    prompt = f"Investiga {prospect_name} en web"  # Minimal
    tools = [web_search]  # Solo tools de web
    # No tiene acceso a vault_lookup, crm_lookup, etc.
```

---

### 3. Max Iterations = 2

**¿Por qué limitar a 2?**

Anti-pattern de tarea-05: sin límite, el agente genera conversaciones largas que inflan contexto.

Con `max_iterations=2`:
- Subagente busca (iteración 1)
- Subagente usa tool (iteración 1)
- Subagente obtiene resultado
- Subagente retorna (fin)

**Máximo 2 rondas de pensamiento por subagente.**

---

### 4. Manejo de Errores

Si un subagente falla:

```python
# Subagente retorna:
{
    "status": "not_found",  # vs "found"
    "data": None,
    "citations": []
}
```

**El coordinador continúa.** No bloquea a los otros subagentes.

---

### 5. Estructura de Output

El coordinador usa una tool final (`structure_result`) para armar JSON estructurado:

```python
def structure_result_handler(prospect_name, web_result, vault_result, contact_result):
    final_result = {
        "prospect_name": prospect_name,
        "investigation": {
            "web": web_result,
            "vault": vault_result,
            "contact": contact_result
        },
        "all_citations": [...]  # Agregar todas las citations
    }
    return final_result
```

---

## ✅ Validación

### Test 1: Prospectus Encontrado (todas las fuentes)
```bash
python coordinator.py
# Input: "Juan García", opción 4
# Esperado: 3 resultados "found"
```

### Test 2: Prospectus No Encontrado
```bash
python coordinator.py
# Input: "Persona Inexistente", opción 1
# Esperado: status "not_found"
```

### Test 3: Seleccionar Una Sola Fuente
```bash
python coordinator.py
# Input: "Juan García", opción 1 (web only)
# Esperado: solo web_result con datos
```

---

## 📊 Observaciones

### Paralelismo vs Secuencial

**Secuencial (sin paralelismo):**
```
Web search: 1s → Vault search: 1s → Contact search: 1s = 3s total
```

**Paralelo (hub-and-spoke):**
```
Web search: 1s
Vault search: 1s  } simultáneamente = ~1s total
Contact search: 1s
```

El coordinador ejecuta los 3 subagentes **en paralelo**, no secuencialmente.

---

## 🔍 Logs & Debug

Para ver el agentic loop en acción:
```bash
python coordinator.py 2>&1 | grep -E "\[coordinator\]|\[.*_agent\]"
```

Output de debug mostrará:
- Iteración del loop
- Tool calls emitidos
- Stop reason
- Resultado final

---

## 🎯 Conceptos Clave a Retener

| Concepto | Implementación |
|----------|---|
| **Hub-and-Spoke** | Coordinador delega a 3 subagentes independientes |
| **Contexto Aislado** | Cada subagente recibe solo su información relevante |
| **Paralelismo** | 3 Tool calls en 1 respuesta del coordinador |
| **Max Iterations** | Limita rondas de pensamiento (anti-pattern tarea-05) |
| **Manejo de errores** | Status codes: "found" vs "not_found" |
| **Agregación** | Tool final estructura el resultado |

---

## Próximos Pasos

1. ✅ Ejecuta `coordinator.py` con diferentes prospects
2. ✅ Experimenta con opciones 1, 2, 3, 4
3. ✅ Revisa logs de debug para entender el agentic loop
4. ✅ Modifica prompts de subagentes y observa cómo cambia el output
5. ✅ Propuesta: Agregar un 4to subagente (ej: "company_research")

