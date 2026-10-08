from django.http import JsonResponse
from decouple import config
import mercadopago

def crear_pago_prueba(request):
    sdk = mercadopago.SDK(config('MP_ACCESS_TOKEN'))

    preference_data = {
        "items": [
            {
                "title": "Pedido de prueba MakerBridge",
                "quantity": 1,
                "unit_price": 100.0,
            }
        ],
        "back_urls": {
            "success": "http://127.0.0.1:8000/pagos/exito/",
            "failure": "http://127.0.0.1:8000/pagos/error/",
            "pending": "http://127.0.0.1:8000/pagos/pendiente/",
        },
    }

    preference_response = sdk.preference().create(preference_data)
    preference = preference_response["response"]

    return JsonResponse({"init_point": preference["init_point"]})