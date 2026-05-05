# Tarea 07 — Hub-and-Spoke con Contexto Aislado

## Objetivo
Implementar un **coordinador** que prepara un brief de prospect lanzando **3 subagentes en paralelo** de forma aislada. Practica paralelismo real, aislamiento de contexto y manejo de errores.

## Contexto
Un coordinador recibe un nombre de prospect y debe:
1. **Subagente Web:** Buscar información pública (LinkedIn, web)
2. **Subagente Vault:** Recuperar historial de interacciones anteriores
3. **Subagente Contact:** Obtener datos de contacto y preferencias

Todos los subagentes **corren en paralelo** en la misma respuesta del coordinador. El coordinador **agrupa** los resultados.

## El Patrón Hub-and-Spoke
```
Coordinador (hub)
    ├─→ Subagente Web (spoke 1)
    ├─→ Subagente Vault (spoke 2)
    └─→ Subagente Contact (spoke 3)
```

## Preguntas Guía
1. ¿Cómo se lanzan 3 Task calls en **una sola respuesta**?
2. ¿Qué significa "contexto aislado" para cada subagente?
3. Si un subagente falla, ¿debería bloquear a los otros?
4. ¿Cómo el coordinador espera a que los 3 terminen antes de continuar?

## El Reto de Paralelismo
- Normalmente: agente A → agente B → agente C (secuencial)
- Aquí: agente A, agente B, agente C **simultáneamente** → agregar resultados

## Estructura Esperada
```
tarea-07/
├── CLAUDE.md (este archivo)
├── README.md (instrucciones y ejecución)
├── coordinator.py (agente coordinador)
├── subagent_web.py (subagente 1)
├── subagent_vault.py (subagente 2)
├── subagent_contact.py (subagente 3)
└── logs/ (validaciones y traces)
```

## Notas
- Python únicamente
- 3 subagentes independientes (3 archivos separados)
- El coordinador hace 3 Task calls en **una respuesta**
- Cada subagente NO debe tener contexto de los otros
- Manejo de errores: si uno falla, los otros continúan
- Documenta el tiempo de paralelismo vs secuencial
