#!/usr/bin/env python3
"""
Coordinador Hub-and-Spoke: Investigación de prospects en paralelo.

TEORÍA:
- El coordinador delega a 3 subagentes simultáneamente (web, vault, contact)
- Cada subagente opera con contexto aislado (solo ve lo que le pasamos)
- El coordinador agrega resultados en una respuesta final
- Max iterations = 2 para limitar contexto generado (tarea-05 anti-pattern)

DECISIONES ARQUITECTÓNICAS:
1. Tool use para delegar búsquedas (web_search, vault_search, contact_search)
2. Tool final (structure_result) para parsear resultado en JSON estructurado
3. Agentic loop: coordinador hace llamadas → espera resultados → continúa
4. Manejo de errores: cada subagente retorna {status, data, citations}
"""

import sys
import os

# Agregar path al SDK (módulo padre)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sdk import client, MODEL
import json

# Los subagentes están implementados en los handlers directamente
# (no necesitamos importarlos porque usamos los handlers inline)

# ============================================================================
# DEFINICIÓN DE TOOLS (Interfaz entre coordinador y subagentes)
# ============================================================================

def get_tools():
    """
    Define las tools que el coordinador usa para delegar.

    TEORÍA: Tools son la interfaz de comunicación entre agentes.
    Cada tool tiene un schema de entrada (qué espera) y cómo procesa output.
    """
    return [
        {
            "name": "web_search",
            "description": "Busca información pública del prospect en web y LinkedIn. Retorna rol, compañía, ubicación, resumen.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "prospect_name": {"type": "string", "description": "Nombre completo del prospect"},
                    "max_iterations": {"type": "integer", "description": "Máximo de páginas de búsqueda (limitado a 2)"}
                },
                "required": ["prospect_name", "max_iterations"]
            }
        },
        {
            "name": "vault_search",
            "description": "Recupera historial de interacciones previas del prospect desde vault (base de datos interna).",
            "input_schema": {
                "type": "object",
                "properties": {
                    "prospect_name": {"type": "string", "description": "Nombre del prospect"},
                    "max_iterations": {"type": "integer", "description": "Máximo de registros a retornar"}
                },
                "required": ["prospect_name", "max_iterations"]
            }
        },
        {
            "name": "contact_search",
            "description": "Obtiene datos de contacto y preferencias de comunicación del prospect.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "prospect_name": {"type": "string", "description": "Nombre del prospect"},
                    "max_iterations": {"type": "integer", "description": "Máximo de intentos"}
                },
                "required": ["prospect_name", "max_iterations"]
            }
        },
        {
            "name": "structure_result",
            "description": "Agrega los resultados de los 3 subagentes en un JSON estructurado final.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "prospect_name": {"type": "string"},
                    "web_result": {"type": "object", "description": "Resultado de web_search"},
                    "vault_result": {"type": "object", "description": "Resultado de vault_search"},
                    "contact_result": {"type": "object", "description": "Resultado de contact_search"}
                },
                "required": ["prospect_name", "web_result", "vault_result", "contact_result"]
            }
        }
    ]


# ============================================================================
# SIMULACIÓN DE SUBAGENTES (Implementación ligera de cada subagente)
# ============================================================================

def web_search_handler(prospect_name: str, max_iterations: int) -> dict:
    """
    Subagente Web - ejecuta búsqueda realista.

    TEORÍA - Contexto Aislado:
    - Solo recibe: prospect_name, max_iterations
    - Solo accede a: data de búsqueda web
    - No ve: vault, contactos, otros resultados
    """
    print(f"[web] Buscando {prospect_name} en web...", file=sys.stderr)

    # Base de datos simulada (como si fuera resultado de búsqueda real)
    fake_web_data = {
        "Juan García": {
            "full_name": "Juan García Pérez",
            "title": "Senior Product Manager",
            "company": "TechCorp Spain",
            "location": "Madrid, España",
            "summary": "Especialista en transformación digital y estrategia de producto. 10+ años en startups y enterprise."
        },
        "María López": {
            "full_name": "María López Martínez",
            "title": "CTO / Principal Engineer",
            "company": "InnovateLabs",
            "location": "Barcelona, España",
            "summary": "Líder técnico con experiencia en cloud infrastructure, Kubernetes, y equipos distribuidos."
        }
    }

    if prospect_name in fake_web_data:
        return {
            "status": "found",
            "data": fake_web_data[prospect_name],
            "citations": [
                {"host": "linkedin.com", "url": f"https://linkedin.com/in/{prospect_name.lower().replace(' ', '-')}"}
            ]
        }
    else:
        return {
            "status": "not_found",
            "data": None,
            "citations": []
        }


def vault_search_handler(prospect_name: str, max_iterations: int) -> dict:
    """
    Subagente Vault - consulta historial interno.

    CONTEXTO AISLADO:
    - Solo accede a: BD interna de interacciones
    - No ve: web research, contactos
    - Retorna: datos mínimos
    """
    print(f"[vault] Consultando historial de {prospect_name}...", file=sys.stderr)

    fake_vault = {
        "Juan García": {
            "last_interaction": "2024-03-15",
            "total_interactions": 3,
            "lead_status": "warm",
            "recent_notes": "Interesado en soluciones B2B de product management"
        },
        "María López": {
            "last_interaction": "2024-04-20",
            "total_interactions": 5,
            "lead_status": "very_warm",
            "recent_notes": "Evaluando herramientas de infraestructura cloud"
        }
    }

    if prospect_name in fake_vault:
        return {
            "status": "found",
            "data": fake_vault[prospect_name],
            "citations": []
        }
    else:
        return {
            "status": "not_found",
            "data": None,
            "citations": []
        }


def contact_search_handler(prospect_name: str, max_iterations: int) -> dict:
    """
    Subagente Contact - obtiene datos de contacto.

    CONTEXTO AISLADO:
    - Solo accede a: BD de contactos (CRM)
    - No ve: web research, vault, otros datos
    - Sensibilidad: solo info pública
    """
    print(f"[contact] Obteniendo contacto de {prospect_name}...", file=sys.stderr)

    fake_contacts = {
        "Juan García": {
            "email": "juan.garcia@techcorp.com",
            "phone": "+34 91 123 4567",
            "timezone": "Europe/Madrid",
            "preferred_contact": "email"
        },
        "María López": {
            "email": "maria.lopez@innovatelabs.com",
            "phone": "+34 93 456 7890",
            "timezone": "Europe/Madrid",
            "preferred_contact": "call"
        }
    }

    if prospect_name in fake_contacts:
        return {
            "status": "found",
            "data": fake_contacts[prospect_name],
            "citations": []
        }
    else:
        return {
            "status": "not_found",
            "data": None,
            "citations": []
        }


def structure_result_handler(prospect_name: str, web_result: dict = None, vault_result: dict = None, contact_result: dict = None) -> dict:
    """
    Agrega los 3 resultados en JSON final estructurado.

    TEORÍA: Este es el punto de agregación del patrón hub-and-spoke.
    El coordinador reúne los 3 resultados aislados en una respuesta cohesiva.
    """
    # Fallback a datos vacíos si no se proporcionan
    web_result = web_result or {"status": "not_found", "data": None, "citations": []}
    vault_result = vault_result or {"status": "not_found", "data": None, "citations": []}
    contact_result = contact_result or {"status": "not_found", "data": None, "citations": []}

    # Agregar todas las citations
    all_citations = []
    for source in [web_result, vault_result, contact_result]:
        if source and source.get("citations"):
            all_citations.extend(source["citations"])

    final_result = {
        "prospect_name": prospect_name,
        "investigation": {
            "web": web_result,
            "vault": vault_result,
            "contact": contact_result
        },
        "all_citations": all_citations,
        "timestamp": "2026-05-04T00:00:00Z"
    }

    return final_result


# ============================================================================
# DISPATCHER: Mapea tool calls a sus implementaciones
# ============================================================================

def handle_tool_call(tool_name: str, tool_input: dict) -> dict:
    """
    Ejecuta la tool solicitada y retorna el resultado.

    ARQUITECTURA: Este dispatcher es el punto central donde cada tool call
    se mapea a su implementación. Permite agregar nuevas sources fácilmente.
    """
    handlers = {
        "web_search": lambda: web_search_handler(tool_input["prospect_name"], tool_input["max_iterations"]),
        "vault_search": lambda: vault_search_handler(tool_input["prospect_name"], tool_input["max_iterations"]),
        "contact_search": lambda: contact_search_handler(tool_input["prospect_name"], tool_input["max_iterations"]),
        "structure_result": lambda: structure_result_handler(
            tool_input["prospect_name"],
            tool_input["web_result"],
            tool_input["vault_result"],
            tool_input["contact_result"]
        )
    }

    if tool_name in handlers:
        return handlers[tool_name]()
    else:
        return {"status": "error", "message": f"Tool {tool_name} not found"}


# ============================================================================
# AGENTIC LOOP: Coordinador con manejo de Tool calls
# ============================================================================

def run_coordinator(prospect_name: str, sources: str) -> dict:
    """
    Ejecuta el loop agentic del coordinador.

    TEORÍA - AGENTIC LOOP:
    1. Coordinador recibe tarea (investigar prospect)
    2. Coordinador decide qué tools usar basado en 'sources'
    3. Emite N tool calls (simultáneamente en la API)
    4. Recibe resultados de tools
    5. Continúa el loop hasta que resuelve (stop_reason = "end_turn")

    PARALELISMO: Los 3 tool calls (web, vault, contact) se emiten en una respuesta.
    La API de Claude los ejecuta en paralelo. Python los recibe juntos y continúa.

    MAX_ITERATIONS = 2: Limita rondas de pensamiento. Anti-pattern de tarea-05.
    """

    # Mapear fuente a tools
    source_map = {
        "1": ["web_search"],
        "2": ["vault_search"],
        "3": ["contact_search"],
        "4": ["web_search", "vault_search", "contact_search"]
    }

    selected_tools = source_map.get(sources, ["web_search", "vault_search", "contact_search"])

    # Armar prompt dinámico basado en selección
    sources_text = {
        "1": "web y LinkedIn",
        "2": "vault (historial interno)",
        "3": "datos de contacto",
        "4": "web, vault y datos de contacto"
    }

    prompt = f"""Eres un coordinador de investigación de prospects.

Tu tarea: Investigar a {prospect_name} en {sources_text.get(sources, 'todas las fuentes')}.

Instrucciones:
1. Usa las tools disponibles para recopilar información en paralelo
2. Cada tool call debe pasar max_iterations=2 para limitar profundidad
3. Después de recibir todos los resultados, usa structure_result para armar el JSON final
4. Retorna el JSON estructurado como respuesta final

Procede ahora."""

    messages = [{"role": "user", "content": prompt}]

    # Loop agentic
    iteration = 0
    max_iterations = 5  # Máximo de rondas del loop
    last_tool_results = {}  # Para almacenar resultados de tools

    while iteration < max_iterations:
        iteration += 1
        print(f"\n[DEBUG] Iteración {iteration} del agentic loop...")

        # Llamada a Claude
        response = client.messages.create(
            model=MODEL,
            max_tokens=2048,
            tools=get_tools(),
            messages=messages
        )

        print(f"[DEBUG] Stop reason: {response.stop_reason}")

        # Procesar respuesta
        tool_calls = []
        text_responses = []

        for block in response.content:
            if block.type == "tool_use":
                tool_calls.append(block)
            elif block.type == "text":
                text_responses.append(block.text)

        # Si no hay tool calls, terminamos
        if not tool_calls:
            print("[DEBUG] No hay tool calls. Fin del loop.")
            if text_responses:
                import re
                last_response = text_responses[-1]
                try:
                    json_match = re.search(r'\{[^{}]*"prospect_name"[^{}]*\}', last_response, re.DOTALL)
                    if json_match:
                        return json.loads(json_match.group())
                except:
                    pass
            break

        # Ejecutar los tool calls en paralelo (Python secuencial, pero Claude los ejecutó en paralelo)
        print(f"[DEBUG] Ejecutando {len(tool_calls)} tool calls...")
        tool_results = []

        for tool_call in tool_calls:
            print(f"  - Ejecutando: {tool_call.name}")
            result = handle_tool_call(tool_call.name, tool_call.input)

            # Guardar resultado para usar luego en structure_result
            if tool_call.name in ["web_search", "vault_search", "contact_search"]:
                last_tool_results[tool_call.name] = result

            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tool_call.id,
                "content": json.dumps(result)
            })

        # Agregar respuesta del coordinador y resultados al historial
        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": tool_results})

        # Verificar stop_reason
        if response.stop_reason == "end_turn":
            print("[DEBUG] Stop reason = end_turn. Terminando loop.")
            break

    # Retornar resultado final con los datos recopilados
    final_result = {
        "prospect_name": prospect_name,
        "investigation": {
            "web": last_tool_results.get("web_search", {"status": "not_found", "data": None, "citations": []}),
            "vault": last_tool_results.get("vault_search", {"status": "not_found", "data": None, "citations": []}),
            "contact": last_tool_results.get("contact_search", {"status": "not_found", "data": None, "citations": []})
        },
        "timestamp": "2026-05-04T00:00:00Z"
    }

    # Agregar todas las citations
    all_citations = []
    for source in ["web_search", "vault_search", "contact_search"]:
        if source in last_tool_results and last_tool_results[source].get("citations"):
            all_citations.extend(last_tool_results[source]["citations"])

    final_result["all_citations"] = all_citations

    return final_result


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("=" * 70)
    print("COORDINADOR HUB-AND-SPOKE - Investigación de Prospects en Paralelo")
    print("=" * 70)

    # Input del usuario
    prospect_name = input("\n¿Nombre del prospect a investigar? ").strip()
    if not prospect_name:
        print("Error: Debes ingresar un nombre.")
        sys.exit(1)

    # Seleccionar fuentes
    print("\n¿Qué fuentes deseas consultar?")
    print("  1) Web/LinkedIn")
    print("  2) Vault (historial interno)")
    print("  3) Datos de contacto")
    print("  4) Todas las fuentes")

    sources = input("\nOpción (1-4): ").strip()
    if sources not in ["1", "2", "3", "4"]:
        print("Error: Opción inválida.")
        sys.exit(1)

    # Ejecutar coordinador
    print(f"\n[INFO] Investigando {prospect_name}...")
    result = run_coordinator(prospect_name, sources)

    # Imprimir resultado final en JSON
    print("\n" + "=" * 70)
    print("RESULTADO FINAL (JSON)")
    print("=" * 70)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
