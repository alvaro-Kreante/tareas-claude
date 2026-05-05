# Tarea 06 — Hooks vs Prompts (Compliance)

## Objetivo
Implementar un agente generador de devis con una **regla de bloqueo determinística** usando PreToolUse hook. Aprender cuándo garantizar compliance via hooks (100% certeza) vs confiar en prompts (probabilístico >90%).

## Contexto
Un agente que genera presupuestos (devis) para clientes. Existe una regla de negocio crítica: **no se pueden ofertar descuentos superiores a 15% a clientes nuevos**. Esta regla debe ser garantizada, no probabilística.

## El Dilema: Hook vs Prompt
- **Prompt:** Decirle al modelo "nunca ofreces >15% descuento a nuevos clientes" → funciona ~95% de las veces
- **Hook:** Interceptar la llamada a herramienta ANTES de ejecutarla y rechazarla si viola la regla → 100% garantía

## Preguntas Guía
1. ¿Cuál es la diferencia entre una rule **probabilística** y una **determinística**?
2. ¿Qué es un PreToolUse hook y cómo interrumpe el flujo?
3. Si confías solo en prompts, ¿qué riesgo legal/empresarial asuistes?
4. ¿Cómo debería el agente saber que su intento fue bloqueado y pueda reintentar?

## La Regla a Implementar
```
SI herramienta = "generar_devis" 
   Y descuento > 15%
   Y cliente_nuevo = true
   ENTONCES bloquear y devolver error
```

## Estructura Esperada
```
tarea-06/
├── CLAUDE.md (este archivo)
├── README.md (instrucciones y ejecución)
├── agent.py (agente + hook implementation)
└── logs/ (validaciones y traces)
```

## Notas
- Python únicamente
- Implementa un hook que valide ANTES de ejecutar la herramienta
- Documenta qué sucede cuando el hook bloquea una acción
- Compara el comportamiento con/sin hook
