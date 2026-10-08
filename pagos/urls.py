from django.urls import path
from . import views

urlpatterns = [
    path('crear/', views.crear_pago_prueba, name='crear_pago_prueba'),
]
