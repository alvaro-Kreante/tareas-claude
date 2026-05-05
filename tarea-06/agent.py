"""
Tarea 06: Hooks vs Prompts
Agente generador de devis con validación de descuentos vía PreToolUse hook
"""

import json
import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

# Cliente Anthropic
client = Anthropic()
MODEL = os.getenv("CLAUDE_MODEL", "claude-haiku-4-5-20251001")

# ============================================================================
# HERRAMIENTAS
# ============================================================================

TOOLS = [
    {
        "name": "generar_devis",
        "description": "Genera un presupuesto (devis) con los parámetros especificados",
        "input_schema": {
            "type": "object",
            "properties": {
                "cliente_id": {"type": "string", "description": "ID del cliente"},
                "descripcion_servicio": {"type": "string", "description": "Descripción del servicio"},
                "monto_base": {"type": "number", "description": "Monto base del presupuesto"},
                "descuento_pct": {"type": "number", "description": "Descuento en porcentaje"},
                "es_cliente_nuevo": {"type": "boolean", "description": "¿Es cliente nuevo?"}
            },
            "required": ["cliente_id", "descripcion_servicio", "monto_base", "descuento_pct", "es_cliente_nuevo"]
        }
    },
    {
        "name": "ajustar_devis",
        "description": "Ajusta los parámetros del devis y reintenta",
        "input_schema": {
            "type": "object",
            "properties": {
                "cliente_id": {"type": "string", "description": "ID del cliente"},
                "descripcion_servicio": {"type": "string", "description": "Descripción del servicio"},
                "monto_base": {"type": "number", "description": "Monto base del presupuesto"},
                "descuento_pct": {"type": "number", "description": "Nuevo descuento en porcentaje"},
                "es_cliente_nuevo": {"type": "boolean", "description": "¿Es cliente nuevo?"}
            },
            "required": ["cliente_id", "descripcion_servicio", "monto_base", "descuento_pct", "es_cliente_nuevo"]
        }
    }
]

# ============================================================================
# HOOK PRETOOLUSE - VALIDACIÓN DETERMINÍSTICA
# ============================================================================

def hook_validar_descuento(tool_name: str, tool_input: dict) -> dict:
    """
    Hook PreToolUse que valida descuentos ANTES de ejecutar la herramienta.
    100% determinístico: si viola la regla, se bloquea.

    Regla: No se pueden ofertar descuentos > 15% a clientes nuevos
    """

    if tool_name not in ["generar_devis", "ajustar_devis"]:
        return None

    descuento = tool_input.get("descuento_pct", 0)
    es_cliente_nuevo = tool_input.get("es_cliente_nuevo", False)

    # Validar regla
    if descuento > 15 and es_cliente_nuevo:
        # ❌ BLOQUEADO
        return {
            "bloqueado": True,
            "status": "amount_exceeds_limit",
            "mensaje": f"❌ RECHAZADO: Descuento máximo para clientes nuevos es 15%. Solicitaste {descuento}%."
        }
    else:
        # ✅ VALIDADO
        return {
            "bloqueado": False,
            "status": "valid_amount",
            "mensaje": "✅ VALIDADO"
        }

# ============================================================================
# EJECUTOR DE HERRAMIENTAS
# ============================================================================

def ejecutar_herramienta(nombre: str, inputs: dict) -> dict:
    """Ejecuta la lógica de la herramienta"""

    monto_base = inputs["monto_base"]
    descuento_pct = inputs["descuento_pct"]
    monto_descuento = monto_base * (descuento_pct / 100)
    monto_final = monto_base - monto_descuento

    return {
        "status": "valid_amount",
        "message": "VALIDADO",
        "devis": {
            "cliente_id": inputs["cliente_id"],
            "descripcion": inputs["descripcion_servicio"],
            "monto_base": monto_base,
            "descuento_pct": descuento_pct,
            "monto_descuento": round(monto_descuento, 2),
            "monto_final": round(monto_final, 2),
            "es_cliente_nuevo": inputs["es_cliente_nuevo"]
        }
    }

# ============================================================================
# CAPTURA DE DATOS DEL USUARIO
# ============================================================================

def capturar_parametros_devis() -> dict:
    """Captura interactivamente el descuento (valores fijos para el resto)"""

    print("\n" + "="*60)
    print("📋 GENERADOR DE DEVIS")
    print("="*60)
    print("Monto base: $1000 (cliente nuevo)\n")

    try:
        descuento = float(input("🎁 Descuento en porcentaje (0-100): "))
        if descuento < 0 or descuento > 100:
            print("Error: Descuento debe estar entre 0 y 100")
            return None
    except ValueError:
        print("Error: Ingresa un número válido")
        return None

    return {
        "cliente_id": "CLI-001",
        "descripcion_servicio": "Servicio estándar",
        "monto_base": 1000,
        "descuento_pct": descuento,
        "es_cliente_nuevo": True
    }

def preguntar_reintentar() -> bool:
    """Pregunta al usuario si desea reintentar con parámetros diferentes"""
    respuesta = input("\n¿Deseas reintentar con parámetros diferentes? (s/n): ").strip().lower()
    return respuesta == 's'

# ============================================================================
# AGENTE PRINCIPAL
# ============================================================================

def ejecutar_agente():
    """Ejecuta el agente generador de devis con validación de hooks"""

    print("\n🤖 Inicializando agente generador de devis...")
    print(f"📦 Modelo: {MODEL}\n")

    # Capturar datos
    datos = capturar_parametros_devis()
    if not datos:
        return

    # Prompt del sistema
    system_prompt = """Eres un asistente profesional de generación de presupuestos (devis).

Tu tarea es:
1. Generar un devis con los parámetros proporcionados usando la herramienta generar_devis
2. Si la herramienta es RECHAZADA (descuento > 15% para cliente nuevo), AUTOMÁTICAMENTE:
   - Reconoce el motivo del rechazo
   - Usa ajustar_devis para intentar con descuento <= 15%
   - Reintenta hasta lograr un devis válido
3. Explica al cliente qué ocurrió y qué ajuste se realizó

IMPORTANTE: Si un descuento es rechazado, NO insistas con el mismo descuento. SIEMPRE ajusta a 15% o menor."""

    user_message = f"""Genera un devis con:
- Monto base: ${datos['monto_base']}
- Descuento: {datos['descuento_pct']}%
- Cliente nuevo: sí

Si el descuento es rechazado, ajusta automáticamente."""

    messages = [{"role": "user", "content": user_message}]

    max_iteraciones = 10
    iteracion = 0

    # Loop agentic
    while iteracion < max_iteraciones:
        iteracion += 1
        print(f"\n{'─'*60}")
        print(f"📍 Iteración {iteracion}/{max_iteraciones}")
        print(f"{'─'*60}")

        # Llamada a Claude
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=system_prompt,
            tools=TOOLS,
            messages=messages
        )

        print(f"Stop Reason: {response.stop_reason}")

        # Procesar respuesta
        if response.stop_reason == "tool_use":
            # El modelo quiere usar una herramienta

            for block in response.content:
                if block.type == "text":
                    print(f"\n💬 Asistente: {block.text}")

                elif block.type == "tool_use":
                    tool_name = block.name
                    tool_input = block.input
                    tool_use_id = block.id

                    print(f"\n🔧 Herramienta: {tool_name}")
                    print(f"   Parámetros: {json.dumps(tool_input, indent=16)}")

                    # HOOK: Validar ANTES de ejecutar
                    resultado_hook = hook_validar_descuento(tool_name, tool_input)

                    if resultado_hook["bloqueado"]:
                        # ❌ Bloqueado por hook
                        print(f"\n{resultado_hook['mensaje']}")
                        tool_result = {
                            "error": resultado_hook["mensaje"],
                            "status": resultado_hook["status"],
                            "bloqueado": True
                        }
                    else:
                        # ✅ Validado, ejecutar
                        print(f"\n{resultado_hook['mensaje']}")
                        tool_result = ejecutar_herramienta(tool_name, tool_input)
                        print(f"\n📊 Devis generado:")
                        print(json.dumps(tool_result["devis"], indent=3, ensure_ascii=False))

                    # Agregar al historial de conversación
                    messages.append({"role": "assistant", "content": response.content})
                    messages.append({
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": tool_use_id,
                                "content": json.dumps(tool_result, ensure_ascii=False)
                            }
                        ]
                    })

        elif response.stop_reason == "end_turn":
            # ✅ Conversación terminada
            print(f"\n{'─'*60}")
            print("✅ PROCESO COMPLETADO")
            print(f"{'─'*60}\n")

            for block in response.content:
                if hasattr(block, 'text'):
                    print(f"💬 Asistente: {block.text}\n")

            # Pregunta de reintento
            if preguntar_reintentar():
                ejecutar_agente()
            break

        else:
            print(f"⚠️  Stop reason desconocido: {response.stop_reason}")
            break

# ============================================================================
# PUNTO DE ENTRADA
# ============================================================================

if __name__ == "__main__":
    ejecutar_agente()
