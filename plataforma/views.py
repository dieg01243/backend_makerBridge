from django.http import JsonResponse
from django.utils import timezone
from .models import Usuario, Pedido, Cotizacion, Pago, LoginHistorial
import json
from django.views.decorators.csrf import csrf_exempt



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




