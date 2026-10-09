from django.urls import path
from . import views

# urlpatterns = [
#     path("auth/register/", views.register_user, name="register_user"), #name="register_user es como un id para la URL de ese enpoint, no es necesario colocarlo pero es buena practica
#     path("auth/login/", views.login_user, name="login_user"),
#     path("makers/", views.ver_lista_de_makers, name="ver_lista_de_makers"),
#     path("makers/me/profile/", views.ver_perfil_maker, name="ver_perfil_maker"),
#     path("makers/me/printers/", views.ver_impresoras_maker, name="ver_impresoras_maker"),
#     path("makers/me/printers/", views.agregar_impresora_maker, name="agregar_impresora_maker"),
# ]

#para probar que funcione
urlpatterns = [
    path("auth/register/", views.register_user, name="register_user"),
    path("auth/login/", views.login_user, name="login_user"),
    path("productos/", views.ver_lista_de_productos, name="ver_lista_de_productos"),
    path("productos/<int:id_producto>/", views.ver_producto, name="ver_producto"),
    path("crear_pedido/", views.crear_pedido, name="crear_pedido"),
]