from django.http import JsonResponse
from django.utils import timezone
from .models import Usuario, Pedido, Cotizacion, Pago, LoginHistorial
import json
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework import status



@csrf_exempt
def register_user(request): #request basicamnete obtiene toda la información que el usuario envía al endpoint, ya sea por GET o POST
#     ej:
#     Ahí request puede contener:
# 
# request.method → "GET", "POST", etc.
# request.body → datos enviados por React.
# request.headers → headers de la petición.
# request.user → usuario autenticado, si corresponde.
# request.GET → parámetros enviados en la URL.
# request.POST → datos de formularios tradicionales.
#==============================================================================
    # Lógica para registrar un nuevo usuario
    


    #verificamos que sea POST
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    #sacar el JSON que mando react
    datos = json.loads(request.body)

    #extraer los datos del JSON
    nombre = datos["nombre"]
    email = datos["email"]
    password = datos["password"]
    rol = datos["rol"]
    activo = True
    fecha_registro = timezone.now()

    #crear objeto y agregarlo a la base de datos
    #aca hace las 2 operaciones a la vez
    #.objet crea el objeto y .create crea el objeto en la base de datos
    usuario = Usuario.objects.create(
        nombre=nombre,
        email=email,
        password_hash=password,
        rol=rol,
        activo=activo,
        fecha_registro=fecha_registro
    )
    
    # 5. Responderle a React
    return JsonResponse({
        "mensaje": "Usuario registrado",
        "id_usuario": usuario.id_usuario
    }, status=201)

def login_user(request):
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    datos = json.loads(request.body)

    email = datos["email"]
    password = datos["password"]

    #con ORM verifica si existe ese mail en la talbla de usuarios
    usuario = Usuario.objects.filter(email=email).first()

    #si no encuentra al usuario
    if usuario is None:
        return Response(
        {"error": "Usuario no encontrado"},
        status=status.HTTP_404_NOT_FOUND
        )
    #si encuentra al usuario, verificamos la contraseña
    if usuario.password_hash != password:
        return Response(
        {"error": "Contraseña incorrecta"},
        status=status.HTTP_401_UNAUTHORIZED
        )

    #se verifico al usuario y ahora se separan los roles
    if usuario.rol == "maker":
        return Response(
            {"mensaje": "Login exitoso", "rol": "maker", "id_usuario": usuario.id_usuario},
            status=status.HTTP_200_OK,
        )

    elif usuario.rol == "cliente":
        return Response(
            {"mensaje": "Login exitoso", "rol": "cliente", "id_usuario": usuario.id_usuario},
            status=status.HTTP_200_OK,
        )

    #========esto no deberia pasar jajaj===========
    return Response(
        {"error": "Rol no permitido"},
        status=status.HTTP_403_FORBIDDEN,
    )
    #==============================================


