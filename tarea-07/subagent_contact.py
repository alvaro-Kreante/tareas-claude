#!/usr/bin/env python3
"""
Subagente Contact - Obtiene datos de contacto y preferencias.

CONTEXTO AISLADO:
- Recibe solo: nombre del prospect, max_iterations
- Accede a: base de datos de contactos (CRM simulado)
- Retorna solo: {status, data, citations}
- NO tiene acceso a web, vault, o contexto del coordinador

TEORÍA:
- Subagente especializado en contacto y preferencias
- Usa tools para consultar CRM/base de contactos
- Sensibilidad: NO retorna todos los datos, solo lo esencial
"""

import sys
import os

# Agregar path al SDK
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sdk import client, MODEL
import json

# ============================================================================
# TOOLS ESPECÍFICAS PARA CONTACTO
# ============================================================================

def get_tools():
    """Tools para obtener datos de contacto."""
    return [
        {
            "name": "crm_lookup",
            "description": "Consulta los datos de contacto y preferencias del prospect en CRM.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "prospect_name": {"type": "string", "description": "Nombre del prospect"},
                    "fields": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Campos a retornar: email, phone, timezone, preferred_contact"
                    }
                },
                "required": ["prospect_name"]
            }
        }
    ]


# ============================================================================
# SIMULACIÓN DE CRM (Base de datos de contactos)
# ============================================================================

def crm_lookup_tool(prospect_name: str, fields: list = None) -> dict:
    """
    Simula consulta a CRM (base de datos de contactos).

    En producción: conectarías a Salesforce, HubSpot, etc.
    """
    crm_db = {
        "Juan García": {
            "email": "juan.garcia@techcorp.com",
            "phone": "+34 91 123 4567",
            "timezone": "Europe/Madrid",
            "preferred_contact": "email",
            "language": "es",
            "company_phone": "+34 91 500 0000"
        },
        "María López": {
            "email": "maria.lopez@innovatelabs.com",
            "phone": "+34 93 456 7890",
            "timezone": "Europe/Madrid",
            "preferred_contact": "call",
            "language": "es",
            "company_phone": "+34 93 400 0000"
        }
    }

    if prospect_name in crm_db:
        contact_data = crm_db[prospect_name]

        # Si se especifican campos, retornar solo esos (sensibilidad)
        if fields:
            filtered = {k: v for k, v in contact_data.items() if k in fields}
        else:
            # Por defecto: solo contacto + preferencia (no datos internos)
            filtered = {
                "email": contact_data.get("email"),
                "phone": contact_data.get("phone"),
                "timezone": contact_data.get("timezone"),
                "preferred_contact": contact_data.get("preferred_contact")
            }

        return {
            "found": True,
            "prospect": prospect_name,
            "data": filtered
        }
    else:
        return {
            "found": False,
            "prospect": prospect_name,
            "data": None
        }


def handle_tool_call(tool_name: str, tool_input: dict) -> dict:
    """Ejecuta la tool solicitada."""
    if tool_name == "crm_lookup":
        result = crm_lookup_tool(
            prospect_name=tool_input.get("prospect_name", ""),
            fields=tool_input.get("fields")
        )
        return result
    else:
        return {"error": f"Tool {tool_name} not found"}


# ============================================================================
# AGENTIC LOOP DEL SUBAGENTE CONTACT
# ============================================================================

def run_contact_agent(prospect_name: str, max_iterations: int = 2) -> dict:
    """
    Agente independiente que obtiene datos de contacto.

    CONTEXTO AISLADO:
    - Input: prospect_name, max_iterations
    - Output: {status, data, citations}
    - NO ve web research, vault, o contexto del coordinador

    TEORÍA - Subagente con sensibilidad de datos:
    - Acceso restringido: solo email, phone, timezone, preferencia
    - No retorna tokens, contraseñas, o datos sensibles
    - Usa tools para consultar CRM de forma segura
    """

    prompt = f"""Necesito que obtengas los datos de contacto de {prospect_name} usando ÚNICAMENTE la herramienta crm_lookup.

NO adivines. DEBES llamar a crm_lookup ahora mismo.

Instrucciones:
1. Llamar a crm_lookup con prospect_name="{prospect_name}", fields=["email", "phone", "timezone", "preferred_contact"]
2. Procesar la respuesta
3. Retornar en JSON exactamente así:
   {{"email": "...", "phone": "...", "timezone": "...", "preferred_contact": "..."}}

Comienza AHORA llamando a crm_lookup."""

    messages = [{"role": "user", "content": prompt}]
    iteration = 0

    while iteration < max_iterations:
        iteration += 1
        print(f"[contact_agent] Iteración {iteration}...", file=sys.stderr)

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
            print(f"[contact_agent] Sin tool calls. Fin.", file=sys.stderr)
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
            print(f"[contact_agent] Stop reason = end_turn", file=sys.stderr)
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
        "status": "found" if data.get("email") else "not_found",
        "data": data,
        "citations": []  # Datos de contacto son internos
    }


# ============================================================================
# MAIN
# ============================================================================

def main():
    if len(sys.argv) < 2:
        print("Uso: python subagent_contact.py <prospect_name> [max_iterations]")
        sys.exit(1)

    prospect_name = sys.argv[1]
    max_iterations = int(sys.argv[2]) if len(sys.argv) > 2 else 2

    print(f"[contact_agent] Obteniendo contacto: {prospect_name}", file=sys.stderr)

    result = run_contact_agent(prospect_name, max_iterations)

    # Retornar JSON al stdout
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
