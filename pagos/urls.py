from django.urls import path
from . import views

urlpatterns = [
    path("crear/<int:id_cotizacion>/", views.crear_pago, name="crear_pago"),
    path("exito/", views.pago_exito, name="pago_exito"),
    path("error/", views.pago_error, name="pago_error"),
    path("pendiente/", views.pago_pendiente, name="pago_pendiente"),
    
]
