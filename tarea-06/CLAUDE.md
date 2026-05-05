# Tarea 06 — Hooks vs Prompts (Compliance)

## Objetivo
Implementar un agente generador de devis con una **regla de bloqueo determinística** usando hook. Aprender cuándo garantizar compliance via hooks (100% certeza) vs confiar en prompts (probabilístico >90%).

## Contexto
Un agente que genera presupuestos (devis) para clientes. Existe una regla de negocio crítica: **no se pueden ofertar descuentos superiores a 15% a clientes nuevos**. Esta regla debe ser garantizada, no probabilística.

## El Dilema: Hook vs Prompt
- **Prompt:** Decirle al modelo "nunca ofreces >15% descuento a nuevos clientes" → funciona ~95% de las veces
- **Hook:** Ejecutar una función Python que bloquea la herramienta ANTES de que Claude la ejecute → 100% garantía

## Conceptos Clave

### ¿Qué es un Hook?
**NO es algo que Claude reconoce automáticamente.** Un hook es:
- Una **función Python** en tu código cliente
- Que se ejecuta **ANTES** de que la herramienta sea llamada
- **100% bajo tu control** — Claude no puede eludir el hook
- Claude solo recibe el resultado: "bloqueado" o "permitido"

### Flujo Detallado
```
1. Usuario solicita descuento 25% (cliente nuevo)
    ↓
2. Claude decide: "Voy a llamar generar_devis(descuento=25%, es_cliente_nuevo=true)"
    ↓
3. [EN TU CÓDIGO] hook_validar_descuento() intercepta la llamada
    ↓
4. Hook evalúa: 25% > 15% AND es_cliente_nuevo → BLOQUEA
    ↓
5. Claude RECIBE error: "Descuento máximo 15%, solicitaste 25%"
    (Claude no sabe que fue un hook, solo sabe que fue rechazado)
    ↓
6. Claude, por su system prompt, decide reintentar
    ↓
7. Claude intenta: generar_devis(descuento=15%, es_cliente_nuevo=true)
    ↓
8. [EN TU CÓDIGO] Hook evalúa: 15% <= 15% → PERMITE
    ↓
9. Claude recibe éxito ✅
    ↓
10. Devis generado con 15%
```

## Preguntas Guía
1. ¿Por qué un hook es **determinístico** pero un prompt es **probabilístico**?
2. ¿Dónde se ejecuta el hook: en Claude o en tu código?
3. ¿Puede Claude "eludir" el hook? ¿Por qué o por qué no?
4. Si confías solo en prompts, ¿qué riesgo empresarial asumes?

## La Regla a Implementar
```
SI herramienta = "generar_devis" o "ajustar_devis"
   Y descuento > 15%
   Y cliente_nuevo = true
   ENTONCES bloquear y devolver error
   
SI cumple:
   ENTONCES permitir
```

## Estructura del Proyecto
```
tarea-06/
├── CLAUDE.md (este archivo)
├── README.md (instrucciones de ejecución)
├── agent.py (agente + hook implementation)
└── logs/ (opcional: traces de ejecución)
```

## Notas de Implementación
- Python únicamente
- El hook es una **función normal** (no una característica especial de Claude)
- Se ejecuta **en tu código**, interceptando la llamada a la herramienta
- Claude nunca ve el código del hook, solo el resultado (error o éxito)
- Documenta qué sucede cuando el hook bloquea
- El error debe ser claro para que Claude sepa cómo ajustar

## Lo Más Importante
Un hook **NO es algo que Claude reconoce o entiende**. Es un patrón de implementación en tu código cliente:
- Intercepta la herramienta ANTES de ejecutarse
- Ejecuta tu lógica de validación
- Bloquea o permite basándose en tu regla
- Claude solo ve el resultado

Esto es lo que hace que sea 100% determinístico.
