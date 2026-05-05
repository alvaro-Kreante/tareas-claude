#!/usr/bin/env python3
"""
Subagente Web - Investigación de prospects en web y LinkedIn.

CONTEXTO AISLADO:
- Recibe solo: nombre del prospect, max_iterations
- Retorna solo: {status, data, citations}
- NO tiene acceso a vault, contactos previos, o contexto del coordinador

TEORÍA:
- Cada subagente es un agente Claude independiente
- Usa tools específicas para su dominio (web_search)
- Genera únicamente lo que el coordinador necesita
"""

import sys
import os

# Agregar path al SDK
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sdk import client, MODEL
import json

# ============================================================================
# TOOLS ESPECÍFICAS PARA WEB SEARCH
# ============================================================================

def get_tools():
    """Tools específicas para búsqueda web."""
    return [
        {
            "name": "web_search",
            "description": "Busca información pública de una persona en web/LinkedIn. Retorna: nombre, título, compañía, ubicación, resumen.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Consulta de búsqueda"},
                    "pages": {"type": "integer", "description": "Número de páginas a consultar (máx 2)"}
                },
                "required": ["query"]
            }
        }
    ]


# ============================================================================
# SIMULACIÓN DE BÚSQUEDA WEB (En producción: SerpAPI, Google Custom Search)
# ============================================================================

def web_search_tool(query: str, pages: int = 1) -> dict:
    """
    Simula búsqueda web realista.

    En producción: llamarías a SerpAPI o Google Custom Search API.
    """
    # Base simulada de resultados
    results_db = {
        "juan garcía linkedin": {
            "full_name": "Juan García Pérez",
            "title": "Senior Product Manager",
            "company": "TechCorp Spain",
            "location": "Madrid, España",
            "summary": "Especialista en transformación digital y estrategia de producto. 10+ años en startups y enterprise.",
            "url": "https://linkedin.com/in/juan-garcia-perez",
            "host": "linkedin.com"
        },
        "maría lópez github": {
            "full_name": "María López Martínez",
            "title": "CTO / Principal Engineer",
            "company": "InnovateLabs",
            "location": "Barcelona, España",
            "summary": "Líder técnico con experiencia en cloud infrastructure, Kubernetes, y equipos distribuidos.",
            "url": "https://github.com/marialopez",
            "host": "github.com"
        }
    }

    # Buscar en la BD simulada
    query_lower = query.lower()
    for key, result in results_db.items():
        if query_lower in key:
            return {
                "found": True,
                "results": [result],
                "pages_searched": min(pages, 2)  # Limitar a 2 páginas
            }

    return {
        "found": False,
        "results": [],
        "pages_searched": 0
    }


def handle_tool_call(tool_name: str, tool_input: dict) -> dict:
    """Ejecuta la tool solicitada."""
    if tool_name == "web_search":
        result = web_search_tool(
            query=tool_input.get("query", ""),
            pages=tool_input.get("pages", 1)
        )
        return result
    else:
        return {"error": f"Tool {tool_name} not found"}


# ============================================================================
# AGENTIC LOOP DEL SUBAGENTE WEB
# ============================================================================

def run_web_agent(prospect_name: str, max_iterations: int = 1) -> dict:
    """
    Agente independiente que busca información web del prospect.

    CONTEXTO AISLADO:
    - Input: prospect_name, max_iterations
    - Output: {status, data, citations}
    - NO ve historial del coordinador, vault, o contactos previos

    TEORÍA - Subagente independiente:
    1. Recibe tarea específica: buscar info web
    2. Usa solo tools para ese dominio
    3. Retorna JSON estructurado
    4. Sin efectos secundarios o contexto externo
    """

    prompt = f"""Necesito que busques información sobre {prospect_name} usando ÚNICAMENTE la herramienta web_search.

NO intentes adivinar ni usar información de memoria. DEBES llamar a web_search ahora mismo.

Instrucciones:
1. Llamar a web_search con query="{prospect_name} linkedin"
2. Analizar resultados
3. Si necesitas más info, llamar nuevamente a web_search
4. Retornar en JSON exactamente así:
   {{"full_name": "...", "title": "...", "company": "...", "location": "...", "summary": "..."}}

Comienza AHORA llamando a web_search."""

    messages = [{"role": "user", "content": prompt}]
    iteration = 0

    tools_available = get_tools()
    print(f"[web_agent] Tools disponibles: {[t['name'] for t in tools_available]}", file=sys.stderr)

    while iteration < max_iterations:
        iteration += 1
        print(f"[web_agent] Iteración {iteration}...", file=sys.stderr)

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
            print(f"[web_agent] Sin tool calls. Respuesta: {text_responses}", file=sys.stderr)
            print(f"[web_agent] Stop reason: {response.stop_reason}", file=sys.stderr)
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
            print(f"[web_agent] Stop reason = end_turn", file=sys.stderr)
            break

    # Parsear resultado final (última respuesta de texto)
    final_text = text_responses[-1] if text_responses else "{}"

    # Intentar extraer JSON
    try:
        # Buscar JSON en la respuesta
        import re
        json_match = re.search(r'\{.*\}', final_text, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
        else:
            data = {}
    except:
        data = {}

    return {
        "status": "found" if data else "not_found",
        "data": data,
        "citations": [
            {"host": "linkedin.com", "url": data.get("url", "https://linkedin.com")},
            {"host": "github.com", "url": "https://github.com"}
        ] if data else []
    }


# ============================================================================
# MAIN
# ============================================================================

def main():
    if len(sys.argv) < 2:
        print("Uso: python subagent_web.py <prospect_name> [max_iterations]")
        sys.exit(1)

    prospect_name = sys.argv[1]
    max_iterations = int(sys.argv[2]) if len(sys.argv) > 2 else 2

    print(f"[web_agent] Investigando: {prospect_name}", file=sys.stderr)

    result = run_web_agent(prospect_name, max_iterations)

    # Retornar JSON al stdout (para que el coordinador lo capture)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
