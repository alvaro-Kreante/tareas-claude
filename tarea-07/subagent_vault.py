#!/usr/bin/env python3
"""
Subagente Vault - Recupera historial de interacciones previas.

CONTEXTO AISLADO:
- Recibe solo: nombre del prospect, max_iterations
- Accede a: base de datos interna (vault.json simulado)
- Retorna solo: {status, data, citations}
- NO tiene acceso a web, contactos, o contexto del coordinador

TEORÍA:
- Este subagente es especialista en historial interno
- No busca en web, solo consulta BD interna
- Retorna datos mínimos y relevantes
"""

import sys
import os

# Agregar path al SDK
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sdk import client, MODEL
import json

# ============================================================================
# TOOLS ESPECÍFICAS PARA VAULT
# ============================================================================

def get_tools():
    """Tools para consultar vault (base de datos interna)."""
    return [
        {
            "name": "vault_lookup",
            "description": "Consulta el historial de interacciones previas del prospect en vault.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "prospect_name": {"type": "string", "description": "Nombre del prospect"},
                    "limit": {"type": "integer", "description": "Máximo de registros a retornar"}
                },
                "required": ["prospect_name"]
            }
        }
    ]


# ============================================================================
# SIMULACIÓN DE VAULT (Base de datos interna)
# ============================================================================

def vault_lookup_tool(prospect_name: str, limit: int = 5) -> dict:
    """
    Simula consulta a vault (BD interna de interacciones).

    En producción: conectarías a una BD real (PostgreSQL, MongoDB, etc).
    """
    vault_db = {
        "Juan García": {
            "interactions": [
                {
                    "date": "2024-03-15",
                    "type": "email",
                    "subject": "Consulta sobre solución B2B",
                    "notes": "Interesado en features de product management"
                },
                {
                    "date": "2024-02-10",
                    "type": "call",
                    "duration": "30 min",
                    "notes": "Presentación de producto. Feedback positivo."
                },
                {
                    "date": "2024-01-20",
                    "type": "email",
                    "subject": "Demo solicitada",
                    "notes": "Primer contacto. Enviar demo link."
                }
            ],
            "total_interactions": 3,
            "last_contact": "2024-03-15",
            "lead_status": "warm"
        },
        "María López": {
            "interactions": [
                {
                    "date": "2024-04-20",
                    "type": "call",
                    "duration": "45 min",
                    "notes": "Evaluando infraestructura cloud. Tech-savvy. Decisora."
                },
                {
                    "date": "2024-03-25",
                    "type": "email",
                    "subject": "ROI Analysis",
                    "notes": "Solicitó análisis de ROI detallado"
                },
                {
                    "date": "2024-02-28",
                    "type": "email",
                    "subject": "Pricing inquiry",
                    "notes": "Preguntó sobre planes enterprise"
                },
                {
                    "date": "2024-02-10",
                    "type": "call",
                    "duration": "20 min",
                    "notes": "Intro call. CTO de startup en growth."
                },
                {
                    "date": "2024-01-15",
                    "type": "email",
                    "subject": "Initial contact",
                    "notes": "Inbound inquiry vía LinkedIn"
                }
            ],
            "total_interactions": 5,
            "last_contact": "2024-04-20",
            "lead_status": "very_warm"
        }
    }

    if prospect_name in vault_db:
        vault_data = vault_db[prospect_name]
        # Limitar a los últimos N registros
        interactions = vault_data["interactions"][:limit]
        return {
            "found": True,
            "prospect": prospect_name,
            "last_interaction": vault_data["last_contact"],
            "total_interactions": vault_data["total_interactions"],
            "lead_status": vault_data["lead_status"],
            "recent_interactions": interactions
        }
    else:
        return {
            "found": False,
            "prospect": prospect_name,
            "last_interaction": None,
            "total_interactions": 0,
            "lead_status": "unknown",
            "recent_interactions": []
        }


def handle_tool_call(tool_name: str, tool_input: dict) -> dict:
    """Ejecuta la tool solicitada."""
    if tool_name == "vault_lookup":
        result = vault_lookup_tool(
            prospect_name=tool_input.get("prospect_name", ""),
            limit=tool_input.get("limit", 5)
        )
        return result
    else:
        return {"error": f"Tool {tool_name} not found"}


# ============================================================================
# AGENTIC LOOP DEL SUBAGENTE VAULT
# ============================================================================

def run_vault_agent(prospect_name: str, max_iterations: int = 2) -> dict:
    """
    Agente independiente que consulta el historial interno (vault).

    CONTEXTO AISLADO:
    - Input: prospect_name, max_iterations
    - Output: {status, data, citations}
    - NO ve web research, contactos, o contexto externo

    TEORÍA - Subagente especializado:
    - Conoce solo su dominio (historial interno)
    - Usa tools para ese dominio
    - Retorna datos estructurados
    """

    prompt = f"""Necesito que consultes el historial interno de {prospect_name} usando ÚNICAMENTE la herramienta vault_lookup.

NO adivines. DEBES llamar a vault_lookup ahora mismo.

Instrucciones:
1. Llamar a vault_lookup con prospect_name="{prospect_name}", limit=5
2. Analizar el historial retornado
3. Retornar en JSON exactamente así:
   {{"last_interaction": "YYYY-MM-DD", "total_interactions": N, "lead_status": "...", "recent_notes": "..."}}

Comienza AHORA llamando a vault_lookup."""

    messages = [{"role": "user", "content": prompt}]
    iteration = 0

    while iteration < max_iterations:
        iteration += 1
        print(f"[vault_agent] Iteración {iteration}...", file=sys.stderr)

        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            tools=get_tools(),
            messages=messages
        )

        # Extraer tool calls y texto
        tool_calls = []
        text_responses = []

        for block in response.content:
            if block.type == "tool_use":
                tool_calls.append(block)
            elif block.type == "text":
                text_responses.append(block.text)

        # Si no hay tool calls, terminar
        if not tool_calls:
            print(f"[vault_agent] Sin tool calls. Fin.", file=sys.stderr)
            break

        # Ejecutar tools
        tool_results = []
        for tool_call in tool_calls:
            result = handle_tool_call(tool_call.name, tool_call.input)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tool_call.id,
                "content": json.dumps(result)
            })

        # Agregar al historial
        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": tool_results})

        if response.stop_reason == "end_turn":
            print(f"[vault_agent] Stop reason = end_turn", file=sys.stderr)
            break

    # Parsear resultado final
    final_text = text_responses[-1] if text_responses else "{}"

    try:
        import re
        json_match = re.search(r'\{.*\}', final_text, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
        else:
            data = {}
    except:
        data = {}

    return {
        "status": "found" if data.get("total_interactions", 0) > 0 else "not_found",
        "data": data,
        "citations": []  # Vault es interno, sin citations públicas
    }


# ============================================================================
# MAIN
# ============================================================================

def main():
    if len(sys.argv) < 2:
        print("Uso: python subagent_vault.py <prospect_name> [max_iterations]")
        sys.exit(1)

    prospect_name = sys.argv[1]
    max_iterations = int(sys.argv[2]) if len(sys.argv) > 2 else 2

    print(f"[vault_agent] Consultando vault: {prospect_name}", file=sys.stderr)

    result = run_vault_agent(prospect_name, max_iterations)

    # Retornar JSON al stdout
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
