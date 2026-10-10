# MakerBridge – Backend

Backend en **Django** (Python) para MakerBridge, una plataforma que conecta clientes con makers de impresión 3D.
Base de datos: **PostgreSQL**. El frontend (React/Vite) corre en `http://localhost:5173`.

## Requisitos

- Python 3.12 o superior
- PostgreSQL (local o remoto, por ejemplo Supabase, Neon o Railway)
- Git

## Instalación

1. Clonar el repositorio y entrar a la carpeta (donde está `manage.py`):

   ```bash
   git clone <URL-DEL-REPO>
   cd backend_makerBridge
   ```

2. Crear y activar un entorno virtual:

   ```powershell
   # Windows (PowerShell)
   py -m venv venv
   .\venv\Scripts\activate
   ```

   ```bash
   # Linux / macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

   Si PowerShell bloquea la activación, ejecutar una vez:
   `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

3. Instalar dependencias:

   ```bash
   pip install -r requirements.txt
   ```

## Configuración

1. Crear un archivo `.env`

2. Completar `.env` con los datos de tu base de datos:

   | Variable      | Descripción                          |
   |---------------|--------------------------------------|
   | `DB_NAME`     | Nombre de la base de datos           |
   | `DB_USER`     | Usuario de PostgreSQL                |
   | `DB_PASSWORD` | Contraseña                           |
   | `DB_HOST`     | Host (`localhost` o el del servicio) |
   | `DB_PORT`     | Puerto (por defecto `5432`)          |

   > El archivo `.env` **no se sube al repositorio**.

## Ejecutar el servidor

```bash
python manage.py runserver
```

La API queda disponible en `http://127.0.0.1:8000/api/`.

## Endpoints disponibles

| Método | Ruta                  | Descripción               |
|--------|-----------------------|---------------------------|
| POST   | `/api/auth/register/` | Registrar un usuario      |
| POST   | `/api/auth/login/`    | Iniciar sesión            |

Ejemplo de registro:

```json
{
  "nombre": "Lucía",
  "email": "lucia@example.com",
  "password": "1234",
  "rol": "cliente"
}
```

El diseño completo de endpoints planificados está en `diseño.txt`.

## Estructura del proyecto

```
backend_makerBridge/
├── api/          # App de prueba
├── config/       # Configuración de Django (settings, urls)
├── plataforma/   # App principal: modelos, vistas y rutas
├── manage.py
├── requirements.txt
└── .env.example
```

## Problemas comunes

- **`ModuleNotFoundError`**: no activaste el entorno virtual o falta `pip install -r requirements.txt`.
- **`password authentication failed` / `connection refused`**: revisá las variables del `.env` y que PostgreSQL esté activo.
- **`relation "usuarios" does not exist`**: falta ejecutar el script SQL de `diseño.txt`.
- **Error de CORS desde el frontend**: el frontend debe correr en `localhost:5173` (ver `CORS_ALLOWED_ORIGINS` en `settings.py`).
