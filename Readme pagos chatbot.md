# MakerBridge — Backend: Pagos y Chatbot
 
Documentación de lo implementado en la rama `pagos`: la **pasarela de pago con Mercado Pago** y el **asistente de IA (chatbot)** para armar solicitudes. Backend en **Django** sobre una base **PostgreSQL en Supabase**.
 
> Este archivo se llama `README_pagos_chatbot.md` a propósito, para no chocar con el `README.md` de instalación que mantiene el equipo en `main`. Más adelante se puede fusionar con ese.
 
---
 
## 1. Qué incluye esta rama
 
| Módulo | Estado | Qué hace |
|---|---|---|
| **Pagos** (`pagos/`) | Funcionando en sandbox | Crea el pago de una cotización aceptada, redirige a Mercado Pago, verifica el resultado y actualiza pago y pedido |
| **Chatbot** (`api/chatbot.py`) | Funcionando en el backend | Asistente que ayuda al cliente a describir su pieza y armar la solicitud |
| Login / registro | En `main` (no está en esta rama) | A cargo de otro integrante del equipo |
 
El circuito crítico de la demo es: **registro/login → solicitud → cotización del maker → pago simulado**. El chatbot se usa en el paso de la solicitud.
 
---
 
## 2. Estructura relevante
 
```
backend_makerBridge/
├── config/            # settings.py y urls.py del proyecto
├── api/               # chatbot.py (asistente con Gemini) y vistas de prueba
├── pagos/             # integración con Mercado Pago
├── plataforma/        # modelos del dominio (Usuario, Pedido, Cotizacion, Pago, ...)
├── requirements.txt
└── .env               # variables secretas (NO se sube a git)
```
 
Rutas principales (`config/urls.py`):
 
| Ruta | Va a |
|---|---|
| `admin/` | Panel de administración de Django |
| `api/hola/` | Vista de prueba |
| `api/chatbot/` | Endpoint del chatbot |
| `pagos/` | Rutas del módulo de pagos (`pagos/urls.py`) |
| `plataforma/` | Rutas del dominio (`plataforma/urls.py`) |
 
---
 
## 3. Instalación y puesta en marcha
 
### 3.1 Clonar y entorno virtual
 
```powershell
git clone <url-del-repo>
cd MakerBridge\BackEnd\backend_makerBridge
git switch pagos
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```
 
Versiones usadas: Python 3.14 y Django 6.1.2 (ver `requirements.txt`).
 
### 3.2 Crear el `.env`
 
En la carpeta del backend (junto a `manage.py`), crear un archivo llamado exactamente `.env` (con el punto y sin extensión):
 
```
DB_NAME=postgres
DB_USER=<usuario del Session pooler de Supabase>
DB_PASSWORD=<contraseña de la base>
DB_HOST=<host del Session pooler>
DB_PORT=5432
 
MP_ACCESS_TOKEN=<Access Token de PRUEBA de Mercado Pago>
BASE_URL=http://127.0.0.1:8000
 
GEMINI_API_KEY=<tu key de Google AI Studio>
```
 
| Variable | Para qué sirve | De dónde sale |
|---|---|---|
| `DB_*` | Conexión a la base compartida | Panel de Supabase → datos de conexión (**Session pooler**) |
| `MP_ACCESS_TOKEN` | Autoriza al backend a crear y consultar pagos | Mercado Pago → Tus integraciones → Credenciales de **prueba** |
| `BASE_URL` | URL pública del backend, para las redirecciones de vuelta desde Mercado Pago | Local: `http://127.0.0.1:8000` (es el valor por defecto) |
| `GEMINI_API_KEY` | Autoriza al backend a consultar a Gemini | aistudio.google.com (gratis) |
 
Detalles:
 
- Se leen con **python-decouple** (`config("NOMBRE")`), no con `os.getenv`.
- Sin espacios alrededor del `=` y sin comillas.
- Cada integrante usa **su propia** `GEMINI_API_KEY`. No se comparten claves.
- Si `DB_PASSWORD` está vacío, `settings.py` cae a SQLite local para poder arrancar sin la base de Supabase.
### 3.3 Levantar el servidor
 
```powershell
python manage.py runserver
```
 
Tiene que decir `Starting development server at http://127.0.0.1:8000/`.
 
---
 
## 4. Base de datos
 
- Base **PostgreSQL en Supabase**, compartida por todo el equipo.
- Tablas ya creadas en Supabase: `usuarios`, `pedidos`, `cotizaciones`, `login_historial` y `pagos`.
- Los modelos de Django (`Usuario`, `Pedido`, `Cotizacion`, `LoginHistorial`, `Pago`) usan `managed = False` y `app_label = "plataforma"`: Django **no crea ni modifica** esas tablas, solo las lee y escribe. Por eso no hacen falta migraciones para ellas.
---
 
## 5. Módulo de pagos (Mercado Pago)
 
### 5.1 Qué resuelve
 
Cobrar una cotización aceptada. El cliente paga el **precio cotizado por el maker** a través de Mercado Pago, y el sistema registra el resultado en la base.
 
### 5.2 Flujo
 
```
1. El cliente acepta una cotización
2. El backend crea un registro Pago (a partir de esa Cotización) y una preferencia de pago en Mercado Pago
3. El cliente es redirigido al checkout de Mercado Pago
4. Mercado Pago lo devuelve a nuestro backend (usa BASE_URL para armar la dirección de vuelta):
   /pagos/exito/ si se aprobó, /pagos/error/ si falló, /pagos/pendiente/ si quedó pendiente
5. pago_exito NO confía en lo que dice la URL: le pregunta a Mercado Pago, con el Access Token, si el pago está realmente aprobado
6. Si está aprobado: se actualizan el Pago (estado y fecha_pago) y el Pedido en Supabase
```
 
### 5.3 Vistas y rutas
 
Definidas en `pagos/urls.py` y publicadas bajo el prefijo `pagos/` (ver `config/urls.py`):
 
| Ruta completa | Vista | Para qué |
|---|---|---|
| `/pagos/crear/<id_cotizacion>/` | `crear_pago` | Crea el Pago a partir de la Cotización indicada (aceptada) y redirige al checkout de Mercado Pago |
| `/pagos/exito/` | `pago_exito` | Recibe al usuario de vuelta y verifica el estado contra Mercado Pago antes de actualizar Pago y Pedido |
| `/pagos/error/` | `pago_error` | Destino al que vuelve el cliente cuando el pago no se concreta |
| `/pagos/pendiente/` | `pago_pendiente` | Destino al que vuelve el cliente cuando el pago queda pendiente de acreditación |
 
Ejemplo: para pagar la cotización número 7, el front lleva al cliente a `http://127.0.0.1:8000/pagos/crear/7/`.
 
### 5.4 Cómo se probó
 
- Con **credenciales de prueba** (sandbox) de Mercado Pago, sin dinero real.
- Se pagó con los usuarios y tarjetas de prueba que da la documentación de Mercado Pago.
- Resultado: el pago quedó **aprobado** y se actualizaron `pagos` y `pedidos` en Supabase.
### 5.5 Decisiones tomadas
 
- **Se cobra el precio cotizado completo.** La comisión del maker **no está implementada en el código** para la demo.
- **Modelo de negocio** (se explica en la defensa, no se calcula en el sistema): al maker se le cobra una comisión por cada pedido; si tiene una suscripción activa (plan premium), no se le cobra la comisión y obtiene otros beneficios.
- La verificación del pago se hace **del lado del servidor** (paso 5 del flujo), porque la URL de retorno la puede editar cualquiera.
---
 
## 6. Chatbot (asistente de solicitudes)
 
### 6.1 Para qué sirve
 
Muchos clientes **no tienen un modelo 3D** y no saben cómo describir lo que necesitan. El asistente conversa con ellos y les hace, de a una, las preguntas que un maker necesita para cotizar: para qué es la pieza, medidas aproximadas, material, cantidad y plazo. Es parte del flujo principal (paso "solicitud"), no un agregado aparte.
 
Usa la **API de Gemini** (capa gratuita de Google AI Studio), con instrucciones propias que lo limitan a MakerBridge e impresión 3D.
 
### 6.2 Contrato de la API
 
```
POST /api/chatbot/
Content-Type: application/json
```
 
Pedido:
 
```json
{
  "messages": [
    { "role": "user", "content": "Necesito un soporte para mi celular" },
    { "role": "assistant", "content": "¿Para qué modelo y dónde lo vas a usar?" },
    { "role": "user", "content": "iPhone 13, para el auto" }
  ]
}
```
 
Respuesta:
 
```json
{ "reply": "Perfecto. ¿Lo querés en un material resistente al calor?" }
```
 
Reglas:
 
- `role` es `"user"` o `"assistant"`.
- El **front guarda el historial** y lo manda completo en cada mensaje: el bot no recuerda nada entre llamadas.
- La lista **debe empezar con un mensaje `user`** (el saludo inicial se muestra en pantalla pero no se envía).
- El backend usa solo los últimos 20 mensajes.
- Siempre responde `200` con `{"reply": ...}`. Si Gemini falla, `reply` trae un mensaje de emergencia y el motivo real se imprime en la terminal del servidor como `Error del chatbot: ...`.
### 6.3 Probarlo
 
```powershell
python -c "import requests; print(requests.post('http://localhost:8000/api/chatbot/', json={'messages':[{'role':'user','content':'Necesito un soporte para mi celular'}]}).text)"
```
 
Para ver la conversación completa de forma gráfica, existe una página de prueba en `http://localhost:8000/api/chatbot/demo/` (solo para desarrollo; hay que **sacarla antes de la entrega**).
 
### 6.4 Detalles técnicos
 
- Modelo actual: `gemini-3.5-flash-lite`. Los nombres de modelo de Gemini cambian seguido; si aparece `404 NOT_FOUND ... model no longer available`, cambiar el nombre en `api/chatbot.py` por otro modelo `flash` disponible para la cuenta.
- La vista usa `@csrf_exempt` para funcionar desde cualquier front: aceptable para la demo, no para producción.
- La key vive solo en el backend. **Nunca** va en el código del front.
- La capa gratuita tiene un límite bajo de uso y Google puede usar esos pedidos para mejorar sus productos: en pruebas, solo datos inventados.
### 6.5 Para conectarlo al front
 
Guía completa (con componente React y versión HTML) en `chatbot-makerbridge.md`. Resumen:
 
- Mandar `POST` con el historial y mostrar `reply`.
- Si el front corre en otro puerto (por ejemplo Vite en `:5173`), hay que habilitar **CORS** en el backend con `django-cors-headers` (`corsheaders` en `INSTALLED_APPS`, el middleware **primero** en `MIDDLEWARE` y el origen del front en `CORS_ALLOWED_ORIGINS`). Todavía **no está aplicado** en esta rama.
---
 
## 7. Conceptos clave (cuándo se usa cada uno)
 
| Concepto | Qué es | Cuándo se usa | Ejemplo de la vida real |
|---|---|---|---|
| **Sandbox (credenciales de prueba)** | Entorno de Mercado Pago que simula pagos sin dinero real | Mientras se desarrolla y se hace la demo | El **simulador de manejo** antes de salir a la calle |
| **Verificar el pago en el servidor** | Preguntarle a Mercado Pago si el pago se aprobó, en lugar de creerle a la URL | Siempre que un pago habilita algo (acá, actualizar el pedido) | Antes de entregar la mercadería, **llamás al banco** para confirmar la transferencia en vez de creerle al comprobante que te muestran |
| **Variables de entorno (`.env`)** | Valores de configuración fuera del código | Claves, contraseñas y datos que cambian entre computadoras | El **papelito con la clave del wifi**: no lo pegás en el cartel del local |
| **`managed = False`** | Le dice a Django que la tabla ya existe y no debe crearla ni cambiarla | Cuando la base la arma otro (acá, el equipo en Supabase) | Alquilás un departamento **ya amoblado**: lo usás, pero no lo remodelás |
| **Historial de mensajes** | Toda la conversación, enviada en cada pedido al bot | Con cualquier IA conversacional, que no recuerda nada sola | Hablar con alguien que se olvida todo al instante y pasarle **el cuaderno con lo conversado** antes de cada pregunta |
 
---
 
## 8. Estado actual y pendientes
 
**Hecho**
 
- [x] Pago con Mercado Pago en sandbox, verificado contra la API y registrado en Supabase.
- [x] Endpoint `POST /api/chatbot/` funcionando con Gemini.
- [x] Ruta del chatbot en `config/urls.py` y librerías en `requirements.txt`.
**Pendiente**
 
- [ ] Conectar el chatbot al front (componente de chat en la pantalla de Nueva Solicitud).
- [ ] Habilitar CORS si el front corre en otro puerto.
- [ ] Unir con `main` (login y registro) y resolver los conflictos de a uno, con el equipo.
- [ ] Sacar la página de prueba `api/chatbot/demo/` antes de la entrega.
- [ ] Revisar que `requirements.txt` esté en UTF-8 (git lo muestra como binario).
- [ ] Opcional: que el bot devuelva los datos de la pieza en JSON para **precargar el formulario** de Nueva Solicitud.
- [ ] Opcional: implementar la comisión del maker y el plan premium (hoy solo se explican).
---
 
## 9. Seguridad
 
- **El `.env` nunca se sube a git.** Contiene la base, Mercado Pago y Gemini. Agregar archivos con `git add <archivo>` uno por uno, sin `git add .`.
- Usar siempre credenciales de **prueba** de Mercado Pago.
- Si alguna credencial se subió alguna vez al repo, considerarla expuesta y regenerarla.
- La API key de Gemini no se pone nunca en el front: todo lo que llega al navegador es visible.
---
 
## 10. Problemas frecuentes
 
| Síntoma | Causa probable | Qué hacer |
|---|---|---|
| `No module named 'X'` al levantar | Falta instalar dependencias | `python -m pip install -r requirements.txt` |
| `UndefinedValueError: ... not found` | Falta una variable en el `.env` | Agregarla con el nombre exacto, sin espacios alrededor del `=` |
| El `.env` "desapareció" tras un cambio de rama | Estaba versionado en algún commit | Restaurarlo desde una copia o rearmarlo con la tabla del punto 3.2 |
| El chatbot responde "Ahora mismo no puedo responder..." | Falló la llamada a Gemini | Ver la línea `Error del chatbot:` en la terminal del servidor |
| Error 404 de modelo en el chatbot | El modelo de Gemini cambió o se retiró | Cambiar el nombre del modelo en `api/chatbot.py` |
| Error 429 en el chatbot | Se pasó el límite de la capa gratuita | Esperar un rato o probar otro modelo `flash` |
| `blocked by CORS policy` en el navegador | Front y back en puertos distintos | Habilitar CORS (ver 6.5) |
| El pago no se actualiza al volver de Mercado Pago | `BASE_URL` no coincide con donde corre el servidor, o el token no es de prueba | Revisar `BASE_URL` y `MP_ACCESS_TOKEN` en el `.env` |
