# Metas API

API REST desarrollada con FastAPI para la gestión de metas personales. Incluye operaciones CRUD, autenticación de usuarios y consultas avanzadas mediante relaciones en base de datos.

---

## Descripción

Esta API permite a los usuarios:

- Crear, consultar, actualizar y eliminar metas personales
- Autenticarse mediante credenciales
- Consultar información combinada mediante JOINs
- Gestionar roles de administrador y usuario

El proyecto implementa buenas prácticas de desarrollo backend: validaciones robustas, manejo de errores y separación clara de responsabilidades.

---

## Tecnologías

- Python 3.10+
- FastAPI
- MySQL
- PyMySQL
- Pydantic
- XAMPP

---

## Requisitos previos

- Python 3.10+ instalado
- XAMPP ejecutándose (Apache y MySQL activos)
- `requirements.txt` disponible

---

## Instalación

```bash
git clone https://github.com/SaulVVelazquez/metas_app.git
cd metas_app
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## Configuración de base de datos

Ejecuta `base.sql` en MySQL (phpMyAdmin o consola):

```sql
-- base.sql contiene:
-- • Base de datos: metas_app
-- • Tablas: usuarios, categorias, metas
-- • Datos de prueba
```

---

## Iniciar servidor

```bash
uvicorn app:app --reload
```

**Acceso:**
- API: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`

---

## Autenticación

**POST** `/login`

```json
{
  "email": "prueba@email.com",
  "password": "123456"
}
```

Headers requeridos en todas las rutas (excepto `/login` y `/register`):
- `x-user-id`: ID del usuario
- `x-rol`: Rol del usuario (`admin` o `user`)

---

## Endpoints principales

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/register` | Registro con hash Bcrypt |
| POST | `/login` | Genera headers de sesión |
| GET | `/metas` | Listado (dinámico por rol) |
| GET | `/metas/{id}` | Obtener por ID |
| POST | `/metas` | Crear con validación 3NF |
| PUT | `/metas/{id}` | Reemplazar |
| PATCH | `/metas/{id}` | Actualizar parcialmente |
| DELETE | `/metas/{id}` | Eliminar |

---

## Esquema de base de datos

### `usuarios`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | INT (PK) | Identificador único |
| nombre | VARCHAR | Nombre completo |
| email | VARCHAR (UNIQUE) | Correo electrónico |
| password | VARCHAR | Hash Bcrypt |
| rol | VARCHAR | `admin` o `user` |

### `categorias`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | INT (PK) | Identificador único |
| nombre | VARCHAR | Nombre categoría |

### `metas`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | INT (PK) | Identificador único |
| usuario_id | INT (FK) | Referencia usuarios |
| categoria_id | INT (FK) | Referencia categorías |
| titulo | VARCHAR | Descripción breve |
| descripcion | TEXT | Detalle completo |
| progreso | INT (0-100) | Porcentaje avance |
| estado | VARCHAR | `pendiente`, `en progreso`, `completado` |
| fecha_inicio | DATE | Inicio objetivo |
| fecha_limite | DATE | Fecha máxima |

---

## Relaciones

- **Usuarios → Metas**: 1:N (un usuario, múltiples metas)
- **Categorías → Metas**: 1:N (una categoría, múltiples metas)

---

## Próximas mejoras

- Implementación JWT
- Middleware de autenticación centralizado
- Paginación de resultados
- Documentación OpenAPI mejorada

---

## Notas

Proyecto técnico con validación de conexión MySQL en `test.py`.
