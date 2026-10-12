import mercadopago
from decouple import config
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone

from plataforma.models import Cotizacion, Pago

BASE_URL = config("BASE_URL", default="http://127.0.0.1:8000")


def _sdk():
    return mercadopago.SDK(config("MP_ACCESS_TOKEN"))


def crear_pago(request, id_cotizacion):
    cotizacion = get_object_or_404(Cotizacion, pk=id_cotizacion)

    if cotizacion.estado != "aceptada":
        return JsonResponse({"error": "La cotización no está aceptada"}, status=400)

    pago, _ = Pago.objects.get_or_create(
        id_cotizacion=cotizacion,
        defaults={
            "monto": cotizacion.precio,
            "metodo_pago": "mercado_pago",
            "estado": "pendiente",
        },
    )
    if pago.estado == "aprobado":
        return JsonResponse({"error": "Esta cotización ya fue pagada"}, status=400)

    preference_data = {
        "items": [
            {
                "title": f"Pedido #{cotizacion.id_pedido_id} - MakerBridge",
                "quantity": 1,
                "unit_price": float(pago.monto),
            }
        ],
        "external_reference": str(pago.id_pago),
        "back_urls": {
            "success": f"{BASE_URL}/pagos/exito/",
            "failure": f"{BASE_URL}/pagos/error/",
            "pending": f"{BASE_URL}/pagos/pendiente/",
        },
    }
    respuesta = _sdk().preference().create(preference_data)["response"]
    return JsonResponse({"id_pago": pago.id_pago, "init_point": respuesta["init_point"]})


def pago_exito(request):
    payment_id = request.GET.get("payment_id")
    if not payment_id:
        return JsonResponse({"error": "Falta payment_id"}, status=400)

    # No confiamos en la URL: le preguntamos a Mercado Pago si de verdad se aprobó
    info = _sdk().payment().get(payment_id)["response"]
    if info.get("status") != "approved":
        return JsonResponse({"estado": info.get("status")})

    with transaction.atomic():
        pago = get_object_or_404(Pago, pk=int(info["external_reference"]))
        pago.estado = "aprobado"
        pago.fecha_pago = timezone.now()
        pago.save(update_fields=["estado", "fecha_pago"])

        pedido = pago.id_cotizacion.id_pedido
        pedido.estado = "en_proceso"
        pedido.save(update_fields=["estado"])

    return JsonResponse({"estado": "aprobado", "id_pago": pago.id_pago})


def pago_error(request):
    return JsonResponse({"estado": "error", "mensaje": "El pago no se pudo completar"})


def pago_pendiente(request):
    return JsonResponse({"estado": "pendiente", "mensaje": "El pago está pendiente"})

from pathlib import Path
from django.http import HttpResponse

