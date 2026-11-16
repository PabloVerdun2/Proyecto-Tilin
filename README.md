# Gourmet — Sistema de Reservas

Aplicación web para la gestión de reservas de un restaurante: registro e inicio de
sesión por correo, menú del local y una API JSON propia para crear y consultar
reservas, persistidas en base de datos.

## Tecnologías

- **Backend:** Python 3.13 · Django 5.2
- **Base de datos:** SQL Server Express (vía `mssql-django` + `pyodbc`)
- **Frontend:** plantillas de Django + JavaScript (sin framework) + CSS
- **Configuración:** variables de entorno con `python-decouple`

## Requisitos previos

- Python 3.13 (o 3.11+)
- SQL Server Express y **ODBC Driver 17 for SQL Server**
- Git

## Instalación

```bash
git clone <url-del-repositorio>
cd Proyecto-Tilin

python -m venv env
# Windows:
env\Scripts\activate
# Linux/Mac:
# source env/bin/activate

pip install -r requirements.txt
```

## Variables de entorno

Copiá `.env.example` como `.env` y completá los valores:

```bash
copy .env.example .env    # Windows
# cp .env.example .env    # Linux/Mac
```

Generá la `SECRET_KEY`:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

El detalle de cada variable (Django y base de datos) está documentado en `.env.example`.

> Nunca subas el `.env`: está en `.gitignore`.

## Preparación de la base de datos

1. Creá una base vacía llamada `GourmetDB` en SQL Server (Django no crea la BD, solo las tablas).
2. Aplicá las migraciones:

```bash
python manage.py migrate
```

3. Creá un usuario administrador:

```bash
python manage.py createsuperuser
```

> El esquema de la base lo generan las migraciones de Django (carpeta `cuentas/migrations/`).

## Comandos de arranque

```bash
python manage.py runserver
```

- **Acceso local:** http://127.0.0.1:8000/
- **Admin de Django:** http://127.0.0.1:8000/admin/

Pruebas de la API:

```bash
python manage.py test cuentas.api.tests
```

## Acceso desplegado

Aún no publicado. Impedimento: la base usa SQL Server con autenticación de
Windows (`trusted_connection`), que no es accesible desde un host de Internet.
Para desplegar: usar `DB_TRUSTED_CONNECTION=no` con usuario/contraseña, o migrar
a un motor en la nube, y definir `DEBUG=False` + `ALLOWED_HOSTS`.

## Funciones

- Registro e inicio de sesión por correo.
- Menú del restaurante.
- Crear y listar reservas mediante la API, con persistencia en base de datos.
- Validaciones de las reservas y pruebas automatizadas de la API.

## Limitaciones

- Los cambios de estado de una reserva no se guardan en la base (solo en `localStorage`).
- Las reservas no asignan mesa automáticamente.
- Los roles existen pero no restringen el acceso a las vistas.
- El proyecto corre en entorno local; aún no está desplegado.
