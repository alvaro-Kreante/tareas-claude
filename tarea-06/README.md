# Tarea 06: Hooks vs Prompts

## 📋 Descripción
Agente generador de devis (presupuestos) con validación determinística de descuentos usando **hook**.

**Regla de negocio:** No se pueden ofertar descuentos > 15% a clientes nuevos.

## 🎯 Conceptos Clave

### Probabilístico vs Determinístico
- **Prompt (Probabilístico):** "No hagas descuentos > 15%" → funciona ~95%
- **Hook (Determinístico):** Función Python que bloquea ANTES de ejecutar → 100% garantía

### ¿Qué es un Hook?
**NO es algo que Claude reconoce automáticamente.** Es:
- Una **función Python** ejecutada en TU código
- Que se ejecuta **ANTES** de que la herramienta se llame
- **100% bajo tu control** — Claude no puede eludir el hook

### Por qué importa
En banca, seguros y compliance, el 5% de margen de error es **inaceptable**. El hook garantiza compliance porque está bajo tu control, no bajo el de Claude.

## 🛠️ Flujo Real

```
Usuario: "Descuento 25%"
    ↓
Claude quiere llamar generar_devis(descuento=25%)
    ↓
[TU CÓDIGO intercepta: hook_validar_descuento()]
    ↓
Hook evalúa: 25% > 15% → BLOQUEA
    ↓
Claude RECIBE error: "Descuento máximo 15%"
    ↓
Claude (por su prompt) reintenta con descuento=15%
    ↓
[TU CÓDIGO] Hook evalúa: 15% <= 15% → PERMITE
    ↓
✅ Devis generado
```

## 📂 Archivos

- `agent.py` — Agente con hook y herramientas
- `CLAUDE.md` — Contexto teórico
- `README.md` — Este archivo

## 🚀 Ejecución

```bash
cd tarea-06
python agent.py
```

Te pide solo el descuento %. Monto base: $1000 (cliente nuevo).

## 📝 Casos de Prueba

### Caso 1: Válido (≤15%)
```
Descuento: 10%
→ ✅ Pasa directo
```

### Caso 2: Bloqueado (>15%)
```
Descuento: 25%
→ ❌ Hook bloquea
→ 🔄 Claude reintenta con 15%
→ ✅ Generado con 15%
```

## 🔍 Qué Observar

- **"❌ RECHAZADO"**: Tu hook ejecutándose en tu código
- **"✅ VALIDADO"**: Significa que pasó la validación del hook
- **Stop Reason**: `tool_use` (quiere usar herramienta), `end_turn` (terminó)
- **Reintento automático**: Claude reintenta porque recibió un error claro

## 📚 Lección Clave

El hook NO es una característica de Claude. Es una **función en tu código cliente** que:
1. Intercepta la llamada a herramienta
2. Valida según tu lógica
3. Bloquea o permite
4. Claude recibe solo el resultado (error o éxito)

Esto es 100% determinístico porque está bajo tu control total.
