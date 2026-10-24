import json
from decouple import config
from google import genai
from google.genai import types
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

client = genai.Client(api_key=config("GEMINI_API_KEY"))

SYSTEM_PROMPT = """Sos el asistente de MakerBridge, una plataforma que conecta clientes
que necesitan piezas impresas en 3D con makers (dueños de impresoras 3D).
Ayudás al cliente a armar su solicitud: preguntá de a una cosa por vez para
averiguar para qué es la pieza, medidas aproximadas, material, cantidad y plazo.
Si no tiene modelo 3D, ayudalo a describir la pieza con sus palabras.
Respondé en español rioplatense, corto y claro. Si preguntan algo que no
tiene que ver con MakerBridge o la impresión 3D, decí amablemente que no podés ayudar con eso."""

RESPUESTA_EMERGENCIA = "Ahora mismo no puedo responder. Probá de nuevo en un rato o cargá la solicitud con el formulario."


@csrf_exempt  # solo para la demo
@require_POST
def chatbot(request):
    body = json.loads(request.body)
    mensajes = body.get("messages", [])[-20:]

    # Gemini usa el rol "model" en lugar de "assistant"
    contents = [
        types.Content(
            role="model" if m["role"] == "assistant" else "user",
            parts=[types.Part(text=m["content"])],
        )
        for m in mensajes
    ]

    try:
        resp = client.models.generate_content(
           model="gemini-3.5-flash-lite",  # confirmá en AI Studio qué modelo tenés gratis
            contents=contents,
            config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
        )
        return JsonResponse({"reply": resp.text})
    except Exception as e:
        print("Error del chatbot:", e)
        return JsonResponse({"reply": RESPUESTA_EMERGENCIA})
