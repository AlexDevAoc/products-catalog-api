## Products Catalog API

API REST construida con FastAPI y SQLAlchemy para gestionar un catálogo de productos con autenticación JWT, control de roles y permisos (RBAC), auditoría de cambios (productos y usuarios) y notificaciones por correo a administradores usando SendGrid.

### Características principales
- Autenticación y sesiones (JWT + registro de sesiones, soporte usuario anónimo)
- Roles y Permisos (admin, anonymous, permisos FULL_ACCESS / READ_PRODUCTS)
- Gestión de Usuarios (CRUD parcial, soft delete, cambio de contraseña)
- Gestión de Productos y Marcas
- Auditoría de cambios (product_change_logs y user_change_logs) con detalle de campo, valor anterior y nuevo
- Notificaciones a administradores (tabla `admin_notifications`) para cambios de productos y usuarios (polimórfica: `change_log_id` o `user_change_log_id`)
- Seed inicial opcional de roles, permisos, usuarios y productos
- Envío de emails con SendGrid (agrupa múltiples cambios en un solo correo)
- Docker / docker-compose listo para levantar API + Postgres

### Arquitectura rápida
```
FastAPI
 ├── Auth (JWT, hashing, sesiones)
 ├── Roles & Permisos (RBAC)
 ├── Productos & Marcas
 ├── Auditoría (ProductChangeLog / UserChangeLog)
 ├── Notificaciones Admin (AdminNotification)
 └── Semillas (seed + seed_products)

```

### Requisitos
- Python 3.11+
- Poetry (opcional) o pip usando `requirements.txt`
- Docker / Docker Compose (opcional para entorno contenerizado)
- Cuenta SendGrid (para notificaciones) y sender verificado se proporciona correo en .env

### Consideraciones
Se puede usar SQLite colocando en la variable de conexion algo como esto `DATABASE_URL="sqlite:///./products-catalog.db"`

### Instalación (local con Poetry)
```bash
poetry install
poetry run uvicorn src.main:app --reload

o

poetry install
eval $(poetry env activate)
uvicorn src.main:app --reload
```

### Instalación (usando requirements.txt)
```bash
python3 -m venv .venv 
source .venv/bin/activate
pip install -r requirements.txt
uvicorn src.main:app --reload
```

### Ejecución con Docker
```bash
docker compose up --build
```
La API quedará en http://localhost:8000

### Documentación interactiva
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Variables de entorno clave
| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| DATABASE_URL | Cadena conexión SQLAlchemy | postgresql+psycopg2://postgres:postgres@db:5432/products-catalog | 
| SECRET_KEY | Clave JWT | cadena_larga_segura |
| ALGORITHM | Algoritmo JWT | HS256 |
| ACCESS_TOKEN_EXPIRE_MINUTES | Minutos expiración token | 60 |
| RUN_SEED | Ejecutar seed base | true/false |
| RUN_SEED_PRODUCTS | Ejecutar seed productos | true/false |
| ADMIN_USER_EMAIL | Email admin inicial | admin@example.com |
| DEFAULT_ADMIN_PASSWORD | Password admin inicial | ChangeMe123 |
| ANON_EMAIL | Email usuario anónimo | anonymous@example.com |
| ANON_PASSWORD | Password usuario anónimo | anon123 |
| SENDGRID_API_KEY | API Key SendGrid | SG.xxxxxx |
| NOTIFICATION_SENDER | Remitente verificado | no-reply@tu-dominio.com |
| ENABLE_EMAIL_NOTIFICATIONS | Habilita envío | true/false |

### Flujo de seeding
1. Establece RUN_SEED=true para crear roles, permisos, admin y usuario anónimo.
2. Establece RUN_SEED_PRODUCTS=true para insertar lote inicial de marcas y productos.
3. Ambos procesos son idempotentes (no duplican datos existentes).

### Auditoría y Notificaciones
- Cada cambio de producto genera uno o más registros en `product_change_logs` (un registro por campo modificado).
- Cambios de usuarios (actualización, cambio password, soft delete) generan registros en `user_change_logs`.
- Tras agrupar los diffs de una operación, se envía un solo correo a todos los administradores activos (si ENABLE_EMAIL_NOTIFICATIONS=true y configuración SendGrid válida).
- Se crean filas en `admin_notifications` con estado PENDING y luego se actualiza a SENT o ERROR.
- La tabla tiene dos llaves foráneas opcionales: `change_log_id` (producto) y `user_change_log_id` (usuario). Solo una se rellena por notificación.

### Endpoints principales (resumen)
- Auth: POST /auth/token, POST /auth/register, POST /auth/anonymous-token
- Users: GET/PUT/PATCH/DELETE /users/{id} (soft delete), cambio password, listado
- Roles & Permisos: CRUD roles, asignar rol a usuario
- Products & Brands: CRUD productos, listado, marcas, vistas
- Change Logs: /product-change-logs, /user-change-logs
- Admin Notifications: /admin-notifications (listar, filtrar por estado) *(agregar filtro por tipo es una futura mejora)*

### Seguridad & Acceso
- Rol admin: acceso completo.
- Rol anonymous: limitado a lecturas públicas (productos) según dependencias.
- Validación de permisos y roles en dependencias (`roles/services.py`).

### Testing
Dependencias de test: pytest, pytest-asyncio, httpx.

#### Estructura actual
Tests ubicados en `tests/`:
- `tests/conftest.py`: Configura una base SQLite en memoria reutilizando la misma conexión (StaticPool), crea las tablas y sobreescribe la dependencia `get_db` de FastAPI para aislar los tests de la BD real. También aplica filtros de warnings vía `pytest.ini`.
- `tests/test_users.py`: Escenarios de CRUD parcial de usuarios y cambio de contraseña (incluye helper idempotente para sembrar usuario admin).
- `tests/test_products.py`: Creación, actualización y soft delete de productos (helper idempotente para rol, usuario y marca).


#### Ejecutar tests
Rápido:
```bash
pytest -q
```

Ver salida detallada (sin suprimir warnings):
```bash
pytest -vv
```

Ejecutar un solo archivo:
```bash
pytest tests/test_users.py -q
```

Ejecutar un test específico:
```bash
pytest tests/test_products.py::test_create_product -q
```

#### Filtrado de Warnings
Se suprimen warnings de deprecación específicos (passlib crypt, Config antiguo de Pydantic) mediante `pytest.ini`. Para verlos de nuevo, elimina la línea `addopts = -p no:warnings` o ejecuta:
```bash
pytest -q -p no:warnings=false
```

#### Buenas prácticas adoptadas
- DB en memoria + StaticPool para compartir el mismo estado con menor latencia.
- Dependencias de FastAPI sobreescritas para no tocar Postgres real.
- Seeds idempotentes en tests: evitan duplicados y conflictos de constraint.

#### Próximas mejoras sugeridas de testing
- Agregar tests de endpoints de auditoría (`product_change_logs`, `user_change_logs`).
- Tests de notificaciones admin (mock SendGrid / desactivar envío real).
- Tests de permisos/roles (accesos denegados vs permitidos).
- Medir cobertura y apuntar a >85% en módulos críticos (auth, products, users).

### Licencia
MIT

### Notas finales
Si se deshabilitan notificaciones (`ENABLE_EMAIL_NOTIFICATIONS=false`), el sistema sigue generando logs de auditoría sin enviar correos.

