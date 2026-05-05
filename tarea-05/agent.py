"""
Agente clasificador de leads - Enfoque en stop_reason, no en max_iterations.
Evita 3 anti-patterns: parsear texto, confiar en max_iterations, usar señales textuales.
"""

import json
import os
from pathlib import Path
from anthropic import Anthropic
from dotenv import load_dotenv

# Cargar .env
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
MODEL = os.getenv("CLAUDE_MODEL", "claude-haiku-4-5-20251001")

# Herramientas: ÚNICAS formas de interacción (no parsing de texto)
TOOLS = [
    {
        "name": "buscar_info",
        "description": "Busca informacion del prospect",
        "input_schema": {
            "type": "object",
            "properties": {
                "campo": {"type": "string", "enum": ["nombre", "budget"]}
            },
            "required": ["campo"]
        }
    },
    {
        "name": "clasificar_lead",
        "description": "Clasifica el lead (TERMINA el agente)",
        "input_schema": {
            "type": "object",
            "properties": {
                "prospect_id": {"type": "string"},
                "prioridad": {"type": "string", "enum": ["ALTA", "MEDIA", "BAJA", "REQUIERE_INFO"]},
                "razon": {"type": "string"}
            },
            "required": ["prospect_id", "prioridad", "razon"]
        }
    }
]

def procesar_tool(tool_name, tool_input, prospect_data):
    """Ejecuta herramientas y retorna resultado estructurado."""
    if tool_name == "buscar_info":
        campo = tool_input["campo"]
        valor = prospect_data.get(campo, "N/A")
        return json.dumps({"valor": valor})
    elif tool_name == "clasificar_lead":
        return json.dumps({"status": "clasificado", "prioridad": tool_input["prioridad"]})
    return json.dumps({"error": "herramienta desconocida"})

def clasificar(nombre, budget, max_iterations=5):
    """
    Loop agentico: clasifica un lead con nombre y budget.

    CLAVE:
    - stop_reason="tool_use" -> el modelo quiere usar una herramienta
    - stop_reason="end_turn" -> el modelo termino (sin mas acciones)
    - NUNCA parsees texto del modelo
    - max_iterations es SOLO un fallback de seguridad
    """

    prospect_data = {
        "nombre": nombre,
        "budget": budget
    }

    budget_status = "No especificado" if (budget is None or budget == 0) else f"${budget}"

    prompt = f"""Clasifica este lead de Calendly:
- Nombre: {nombre}
- Budget: {budget_status}

PRIMERO: Usa buscar_info para confirmar nombre y budget.
LUEGO: Clasifica con ALTA, MEDIA, BAJA o REQUIERE_INFO.

Reglas:
- Si budget es 0 o no especificado -> REQUIERE_INFO
- Si budget > 50000 -> ALTA
- Si budget 20000-50000 -> MEDIA
- Si budget < 20000 -> BAJA"""

    messages = [{"role": "user", "content": prompt}]
    historial = []

    for i in range(max_iterations):
        print(f"\n[Iter {i+1}] Llamando modelo...")

        response = client.messages.create(
            model=MODEL,
            max_tokens=500,
            tools=TOOLS,
            messages=messages
        )

        print(f"  stop_reason: {response.stop_reason}")

        # Signal confiable: stop_reason, no texto
        if response.stop_reason == "end_turn":
            print("  -> El modelo termino sin usar herramientas")
            historial.append({"iter": i+1, "stop_reason": "end_turn", "tools": []})
            return {"prioridad": "error_no_clasificado", "historial": historial}

        if response.stop_reason == "tool_use":
            # Procesa las herramientas
            messages.append({"role": "assistant", "content": response.content})

            tools_usadas = []
            tool_results = []

            for block in response.content:
                if block.type == "tool_use":
                    print(f"  -> Usando: {block.name}")
                    result = procesar_tool(block.name, block.input, prospect_data)
                    print(f"    Resultado: {result}")

                    tools_usadas.append({
                        "nombre": block.name,
                        "resultado": result
                    })

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })

                    # Si usó clasificar_lead, ya está hecho
                    if block.name == "clasificar_lead":
                        historial.append({"iter": i+1, "stop_reason": "tool_use", "tools": tools_usadas})
                        return {"prioridad": block.input["prioridad"], "historial": historial}

            # Registra la iteración
            historial.append({"iter": i+1, "stop_reason": "tool_use", "tools": tools_usadas})

            # Añade resultados al contexto
            messages.append({"role": "user", "content": tool_results})

    print(f"  WARN: Alcanzado max_iterations={max_iterations}")
    return {"prioridad": "max_iterations", "historial": historial}

if __name__ == "__main__":
    print("=== Clasificador de Leads ===\n")

    nombre = input("Nombre del lead: ")
    budget_input = input("Budget (numero o 'ninguno'): ")
    budget = float(budget_input) if budget_input.lower() != "ninguno" else None

    resultado = clasificar(nombre, budget)

    print(f"\n=== RESULTADO ===")
    print(f"Prioridad: {resultado['prioridad']}")
