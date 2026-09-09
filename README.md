# 📦 Gestor de Recetas - Black Desert Craft

Sistema de gestión de recetas de crafteo para **Black Desert**. Permite crear items, definir recetas con ingredientes y sub-recetas, y calcular los materiales necesarios para fabricar una cantidad determinada teniendo en cuenta el inventario disponible.

## Tecnologías

- Python 3.10+
- Django 4.2
- SQLite para despliegue gratuito / PostgreSQL opcional para desarrollo local
- Django ORM
- HTML5 + Bootstrap 5 (CDN)

## Despliegue gratuito en PythonAnywhere

La rama `pythonanywhere-free` está preparada para ejecutar la aplicación con SQLite, evitando la dependencia de PostgreSQL.

### 1. Clonar el repositorio

En una consola Bash de PythonAnywhere:

```bash
git clone -b pythonanywhere-free https://github.com/reivincitot/items_crud.git
cd items_crud/Items_Calculator
```

### 2. Crear entorno virtual con Python 3.10

```bash
mkvirtualenv --python=/usr/bin/python3.10 items-crud-env
pip install -r ../../requirements.txt
```

Si el comando anterior no coincide con la ruta de Python disponible en tu cuenta, selecciona Python 3.10 al crear el virtualenv desde PythonAnywhere y utiliza ese entorno.

### 3. Migrar SQLite

```bash
python manage.py migrate
```

### 4. Crear usuario administrador (opcional)

```bash
python manage.py createsuperuser
```

### 5. Recopilar archivos estáticos

```bash
python manage.py collectstatic --noinput
```

### 6. Configuración de la aplicación web

- Framework: Django
- Python: 3.10
- Virtualenv: `items-crud-env`
- WSGI: `Items_Calculator/Items_Calculator/wsgi.py`
- Directorio de trabajo: `.../items_crud/Items_Calculator`

En el archivo WSGI de PythonAnywhere, añade la ruta del proyecto si es necesario:

```python
import os
import sys

path = '/home/TU_USUARIO/items_crud/Items_Calculator'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Items_Calculator.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

Configura las variables de entorno de producción:

```text
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=<una-clave-secreta-nueva>
DJANGO_ALLOWED_HOSTS=<tu-usuario>.pythonanywhere.com
DJANGO_DB=sqlite
```

### Archivos estáticos

En la sección Static files de PythonAnywhere:

```text
URL: /static/
Directory: /home/TU_USUARIO/items_crud/Items_Calculator/staticfiles
```

Luego recarga la aplicación web.

## Desarrollo local con PostgreSQL

Si quieres continuar usando PostgreSQL en tu PC, instala las dependencias correspondientes y configura:

```text
DJANGO_DB=postgresql
POSTGRES_DB=recipes_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=tu-clave
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

La configuración de Django seleccionará PostgreSQL cuando `DJANGO_DB=postgresql`; de lo contrario utilizará SQLite.

## Funcionalidades

- CRUD de items.
- Categorías, tipos y subtipos.
- Indicador de item fabricable.
- CRUD de recetas.
- Recetas con múltiples ingredientes.
- Recetas que pueden producir más de una unidad por lote.
- Cálculo recursivo de materiales.
- Detección de ciclos en recetas.
- Inventario inicial para descontar materiales.
- Árbol jerárquico de producción.
- Autocompletado de items.
- Mensajes de éxito y error.
