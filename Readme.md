# Metas API

API REST desarrollada con FastAPI para la gestión de metas personales. Permite realizar operaciones CRUD, autenticación de usuarios y consultas avanzadas mediante relaciones en base de datos.

---

##  Descripción

Esta API permite a los usuarios:

- Crear, consultar, actualizar y eliminar metas personales
- Autenticarse mediante login
- Consultar información combinada mediante JOIN

El proyecto sigue buenas prácticas de desarrollo backend con validaciones, manejo de errores y separación de responsabilidades.

---

##  Tecnologías utilizadas

- Python 3.14.4
- FastAPI
- MySQL
- PyMySQL
- Pydantic
- XAMPP

---

##  Requisitos previos

- Python 3.14.4 instalado
- XAMPP en ejecución (Apache y MySQL activos)
- Archivo `requirements.txt`

---

##  Instalación rápida

```bash
git clone https://github.com/SaulVVelazquez/metas_app.git
cd metas_app
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

---

##  Configuración de base de datos

Ejecuta el archivo `base.sql` en MySQL (phpMyAdmin o consola) para:
- Crear la base de datos `metas_app`
- Crear tablas (`usuarios`, `categorias`, `metas`)
- Cargar datos de prueba

---

##  Iniciar servidor

```bash
uvicorn app:app --reload
```

**Acceso:**
- **API:** http://localhost:8000
- **Swagger:** http://localhost:8000/docs

---

##  Autenticación

**POST** `/login`
```json
{
  "email": "prueba@email.com",
  "password": "123456"
}
```

---

##  Endpoints principales

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | /metas | Obtener todas |
| GET | /metas/{id} | Obtener por ID |
| POST | /metas | Crear |
| PUT | /metas/{id} | Reemplazar |
| PATCH | /metas/{id} | Actualizar parcialmente |
| DELETE | /metas/{id} | Eliminar |

- `POST /register`: Registro de usuarios (Hasheo de password con Bcrypt).
- `POST /login`: Genera respuesta con headers de sesión.
- `GET /metas`: Listado dinámico (Admin ve todo / User ve lo suyo).
- `POST /metas`: Creación con validación de integridad 3NF.
- `PUT /metas/{id}`: Actualización de progreso y estados.
- `DELETE /metas/{id}`: Borrado físico de registros.

*Nota: Todas las rutas (excepto login/register) requieren headers `x-user-id` y `x-rol`.*
---

##  Esquema de base de datos

La base de datos `metas_app` está compuesta por tres tablas principales vinculadas mediante llaves foráneas.

### 1. Tabla: `usuarios`
Almacena la información de acceso y perfil de los usuarios del sistema.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | Integer (PK, Auto-increment) | Identificador único |
| nombre | Varchar | Nombre completo |
| email | Varchar | Correo electrónico único |
| password | Varchar | Contraseña encriptada |
| rol | Varchar | Permisos (`admin` o `user`) |

### 2. Tabla: `categorias`
Clasifica las metas para normalización de datos.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | Integer (PK, Auto-increment) | Identificador único |
| nombre | Varchar | Nombre de categoría (ej. "Personal", "Laboral") |

### 3. Tabla: `metas`
Contiene los objetivos de cada usuario.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | Integer (PK, Auto-increment) | Identificador único |
| usuario_id | Integer (FK) | Referencia a `usuarios` |
| categoria_id | Integer (FK) | Referencia a `categorias` |
| titulo | Varchar | Nombre descriptivo |
| descripcion | Text | Detalle de la meta |
| progreso | Integer | Porcentaje (0-100) |
| estado | Varchar | Estado (`pendiente`, `en progreso`, `completado`) |
| fecha_inicio | Date | Inicio del objetivo |
| fecha_limite | Date | Fecha máxima de cumplimiento |

---

##  Relaciones y cardinalidad

- **Usuarios → Metas (1:N):** Un usuario puede tener múltiples metas
- **Categorías → Metas (1:N):** Una categoría puede clasificar múltiples metas

---

##  Mejoras futuras

- Implementación de JWT
- Middleware de autenticación
- Paginación de resultados

---

##  Notas

Proyecto desarrollado como prueba técnica. Incluye `test.py` para verificar conexión a MySQL.
