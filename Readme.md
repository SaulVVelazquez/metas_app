#  Metas API

API REST desarrollada con FastAPI para la gestión de metas personales. Permite realizar operaciones CRUD, autenticación de usuarios y consultas avanzadas mediante relaciones en base de datos.

---

## Descripción

Esta API permite a los usuarios:

* Crear metas personales
* Consultar metas
* Actualizar metas (total o parcialmente)
* Eliminar metas
* Autenticarse mediante login
* Consultar información combinada mediante JOIN

El proyecto está diseñado siguiendo buenas prácticas de desarrollo backend, utilizando validaciones, manejo de errores y separación de responsabilidades.

---

##  Tecnologías utilizadas

* Python 3.14.4
* FastAPI
* MySQL
* PyMySQL
* Pydantic
* XAMPP (para servidor MySQL)

---

##  Requisitos

Antes de ejecutar el proyecto, asegúrate de tener:

* Python 3.14.4 instalado
* XAMPP en ejecución (Apache y MySQL activos)
* MySQL corriendo en localhost
* Archivo `requirements.txt`

---

## Instalación

### 1. Clonar repositorio

```bash id="n9hr3y"
git clone https://github.com/SaulVVelazquez/metas_app.git
cd metas_app
```

---

### 2. Crear entorno virtual (opcional)

```bash id="2k7qsu"
python -m venv venv
venv\Scripts\activate
```

---

### 3. Instalar dependencias

```bash id="6c8l5r"
pip install -r requirements.txt
```

---

### 4. Configurar base de datos

En el proyecto se incluye un archivo:

```id="8t3o6u"
base.sql
```

Este archivo contiene:

* Creación de la base de datos `metas_app`
* Creación de tablas (`usuarios`, `categorias`, `metas`)
* Datos de prueba (seed)

👉 Ejecuta este archivo en MySQL (phpMyAdmin o consola)

---

### 5. Ejecutar servidor

```bash id="9r4sn1"
uvicorn app:app --reload
```

---

##  Acceso

* API:

```id="c3d5jq"
http://localhost:8000
```

* Documentación interactiva (Swagger):

```
http://localhost:8000/docs
```

---

##  Base de datos

Nombre:

```
metas_app
```

### Tablas principales:

* usuarios
* categorias
* metas

### Relaciones:

* Un usuario puede tener múltiples metas
* Una categoría puede contener múltiples metas

---

##  Autenticación

### Endpoint:

```
POST /login
```

### Ejemplo:

```json id="q5m2qf"
{
  "email": "prueba@email.com",
  "password": "123456"
}
```

---

##  Endpoints

###  Metas

| Método | Endpoint            | Descripción             |
| ------ | ------------------- | ----------------------- |
| GET    | /metas              | Obtener todas las metas |
| GET    | /metas/{id}         | Obtener meta por ID     |
| GET    | /metas/usuario/{id} | Metas por usuario       |
| GET    | /metas-detalle      | Consulta con JOIN       |
| POST   | /metas              | Crear meta              |
| PUT    | /metas/{id}         | Reemplazar meta         |
| PATCH  | /metas/{id}         | Actualizar parcialmente |
| DELETE | /metas/{id}         | Eliminar meta           |

---

## Ejemplo de consumo

### GET

```bash id="rjw7sx"
curl http://localhost:8000/metas
```

---

### POST

```bash id="r5y64q"
curl -X POST http://localhost:8000/metas \
-H "Content-Type: application/json" \
-d '{
  "usuario_id":1,
  "categoria_id":1,
  "titulo":"Nueva meta",
  "descripcion":"Ejemplo",
  "progreso":0,
  "estado":"pendiente"
}'
```

---

##  Características

* CRUD completo
* Validación de datos con Pydantic
* Manejo de errores HTTP
* Consultas avanzadas con JOIN
* API REST estructurada
* Código organizado

---

## 🚀 Posibles mejoras futuras

* Implementación de JWT
* Hash de contraseñas
* Middleware de autenticación
* Paginación de resultados

---

## 📌 Notas

Este proyecto fue desarrollado como parte de una prueba técnica para demostrar habilidades en desarrollo backend con FastAPI, bases de datos relacionales y diseño de APIs.

##  Archivo de prueba de conexión

El proyecto incluye un archivo adicional:

```bash
test.py
```

Este archivo se utilizó para verificar la conexión a la base de datos MySQL de forma independiente antes de integrar la lógica en la API.

Permite validar:

* Conexión correcta a la base de datos
* Credenciales de acceso
* Disponibilidad del servidor MySQL (XAMPP)

Este archivo es útil durante el desarrollo para pruebas y depuración.

