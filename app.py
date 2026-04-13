from fastapi import FastAPI, HTTPException, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Literal
import pymysql
import bcrypt

# ======================
# CONEXION
# ======================
def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="metas_app",
        cursorclass=pymysql.cursors.DictCursor
    )

# ======================
# PASSWORD
# ======================
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False

# ======================
# MODELOS
# ======================
class UsuarioIN(BaseModel):
    nombre: str = Field(..., example="Juan Perez")
    email: EmailStr = Field(..., example="juan@email.com")
    password: str = Field(..., min_length=6, example="123456")
    rol: Literal["admin", "user"] = Field(..., example="user")

class Login(BaseModel):
    email: EmailStr = Field(..., example="admin@email.com")
    password: str = Field(..., example="123456")

class CategoriaIN(BaseModel):
    nombre: str = Field(..., example="Salud")

class MetaIN(BaseModel):
    categoria_id: Optional[int] = Field(None, example=1)
    titulo: str = Field(..., example="Aprender FastAPI")
    descripcion: Optional[str] = Field(None, example="Practicar endpoints")
    progreso: int = Field(..., ge=0, le=100, example=40)
    estado: Literal["pendiente", "en progreso", "completado"] = Field(..., example="en progreso")
    fecha_inicio: Optional[str] = Field(None, example="2026-04-10")
    fecha_limite: Optional[str] = Field(None, example="2026-05-01")

# ======================
# APP
# ======================
app = FastAPI(
    title="API Metas con Roles",
    description="""
API REST para gestión de metas personales.

Autenticación mediante headers:
- x-user-id
- x-rol

Roles disponibles:
- admin
- user

admin puede gestionar todo
user solo sus metas
""",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======================
# MIDDLEWARE AUTH
# ======================
@app.middleware("http")
async def auth(request: Request, call_next):
    if request.method == "OPTIONS":
        return await call_next(request)

    rutas_publicas = ["/", "/login", "/register", "/docs", "/openapi.json"]

    if request.url.path in rutas_publicas:
        return await call_next(request)

    user_id = request.headers.get("x-user-id")
    rol = request.headers.get("x-rol")

    if not user_id or not rol:
        return JSONResponse(status_code=401, content={"detail": "Falta autenticación"})

    request.state.user_id = int(user_id)
    request.state.rol = rol
    return await call_next(request)

# ======================
# ROOT
# ======================
@app.get("/", tags=["Sistema"], summary="Verificar estado API", description="Endpoint público para verificar que la API está activa.")
def home():
    return {"mensaje": "API funcionando correctamente"}

# ======================
# AUTH
# ======================
@app.post("/register", tags=["Auth"], summary="Registrar usuario", description="Endpoint público para crear nuevos usuarios.")
def register(user: UsuarioIN):
    conn = get_connection()

    with conn.cursor() as cursor:
        cursor.execute("SELECT id FROM usuarios WHERE email=%s", (user.email,))

        if cursor.fetchone():
            raise HTTPException(400, "Email ya registrado")

        hashed = hash_password(user.password)

        cursor.execute(
            "INSERT INTO usuarios (nombre,email,password,rol) VALUES(%s,%s,%s,%s)",
            (user.nombre, user.email, hashed, user.rol)
        )

    conn.commit()
    conn.close()

    return {"mensaje": "Usuario creado correctamente"}

@app.post("/login", tags=["Auth"], summary="Login usuario", description=" login usuario. Devuelve headers necesarios para autenticación.")
def login(data: Login):
    conn = get_connection()

    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM usuarios WHERE email=%s", (data.email,))
        user = cursor.fetchone()

    conn.close()

    if not user:
        raise HTTPException(401, "Credenciales incorrectas")

    if not verify_password(data.password, user["password"]):
        raise HTTPException(401, "Credenciales incorrectas")

    return {"x-user-id": user["id"], "x-rol": user["rol"], "nombre": user["nombre"]}

# ======================
# CATEGORIAS
# ======================
@app.get("/categorias", tags=["Categorias"], summary="Obtener categorías", description="Roles permitidos: admin, user. Headers requeridos: x-user-id, x-rol")
def get_categorias(
    request: Request,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None)
):
    conn = get_connection()

    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM categorias")
        data = cursor.fetchall()

    conn.close()

    return data


@app.post("/categorias", tags=["Categorias"])
def create_categoria(
    cat: CategoriaIN,
    request: Request,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None)
):
    if request.state.rol != "admin":
        raise HTTPException(403, "Solo los administradores pueden crear categorías")

    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("INSERT INTO categorias (nombre) VALUES (%s)", (cat.nombre,))
    conn.commit()
    conn.close()
    return {"mensaje": "Categoría creada"}

# ======================
# METAS
# ======================
@app.get("/metas", tags=["Metas"], summary="Obtener metas", description="admin → todas las metas, user → solo sus metas. Headers requeridos: x-user-id, x-rol")
def get_metas(
    request: Request,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None)
):
    user_id = request.state.user_id
    rol = request.state.rol

    conn = get_connection()

    with conn.cursor() as cursor:
        if rol == "admin":
            cursor.execute("""
                SELECT m.*, u.nombre nombre_usuario, c.nombre nombre_categoria
                FROM metas m
                INNER JOIN usuarios u ON m.usuario_id = u.id
                LEFT JOIN categorias c ON m.categoria_id = c.id
            """)
        else:
            cursor.execute("""
                SELECT m.*, u.nombre nombre_usuario, c.nombre nombre_categoria
                FROM metas m
                INNER JOIN usuarios u ON m.usuario_id = u.id
                LEFT JOIN categorias c ON m.categoria_id = c.id
                WHERE m.usuario_id=%s
            """, (user_id,))

        data = cursor.fetchall()

    conn.close()

    return data


@app.post("/metas", tags=["Metas"], summary="Crear meta", description="El usuario_id se asigna automáticamente desde headers.")
def create_meta(
    meta: MetaIN,
    request: Request,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None)
):
    try:
        usuario_id = request.state.user_id

        if meta.fecha_inicio and meta.fecha_limite:
            if meta.fecha_inicio > meta.fecha_limite:
                raise HTTPException(400, "La fecha de inicio no puede ser mayor a la límite")

        estado = meta.estado
        if meta.progreso == 100:
            estado = "completado"

        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO metas 
                (usuario_id, categoria_id, titulo, descripcion, progreso, estado, fecha_inicio, fecha_limite)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                usuario_id,
                meta.categoria_id or 1,
                meta.titulo,
                meta.descripcion or "",
                meta.progreso or 0,
                estado or "pendiente",
                meta.fecha_inicio,
                meta.fecha_limite
            ))
        conn.commit()
        conn.close()
        return {"mensaje": "Meta creada correctamente"}

    except Exception as e:
        print(f"ERROR EN EL BACKEND: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/metas/{id}", tags=["Metas"], summary="Actualizar meta", description="admin: todas las metas, user: solo sus metas")
def update_meta(
    id: int,
    meta: MetaIN,
    request: Request,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None)
):
    user_id = request.state.user_id
    rol = request.state.rol

    if meta.fecha_inicio and meta.fecha_limite:
        if meta.fecha_inicio > meta.fecha_limite:
            raise HTTPException(400, "fecha_inicio mayor que fecha_limite")

    estado = meta.estado
    if meta.progreso == 100:
        estado = "completado"

    conn = get_connection()

    with conn.cursor() as cursor:
        if rol == "user":
            cursor.execute("""
                UPDATE metas
                SET categoria_id=%s, titulo=%s, descripcion=%s, progreso=%s,
                    estado=%s, fecha_inicio=%s, fecha_limite=%s
                WHERE id=%s AND usuario_id=%s
            """, (meta.categoria_id, meta.titulo, meta.descripcion, meta.progreso,estado, meta.fecha_inicio, meta.fecha_limite, id, user_id))
        else:
            cursor.execute("""
                UPDATE metas
                SET categoria_id=%s, titulo=%s, descripcion=%s, progreso=%s,
                    estado=%s, fecha_inicio=%s, fecha_limite=%s
                WHERE id=%s
            """, (meta.categoria_id, meta.titulo, meta.descripcion, meta.progreso,estado, meta.fecha_inicio, meta.fecha_limite, id))

    conn.commit()
    conn.close()

    return {"mensaje": "Meta actualizada correctamente"}


@app.delete("/metas/{id}", tags=["Metas"], summary="Eliminar meta")
def delete_meta(
    id: int,
    request: Request,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None)
):
    user_id = request.state.user_id
    rol = request.state.rol

    conn = get_connection()

    with conn.cursor() as cursor:
        if rol == "user":
            cursor.execute("DELETE FROM metas WHERE id=%s AND usuario_id=%s", (id, user_id))
        else:
            cursor.execute("DELETE FROM metas WHERE id=%s", (id,))

    conn.commit()
    conn.close()

    return {"mensaje": "Meta eliminada correctamente"}

# ======================
# USUARIOS (ADMIN)
# ======================
@app.get("/usuarios", tags=["Usuarios"], summary="Obtener usuarios", description="Solo admin")
def get_users(
    request: Request,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None)
):
    if request.state.rol != "admin":
        raise HTTPException(403, "Solo admin")

    conn = get_connection()

    with conn.cursor() as cursor:
        cursor.execute("SELECT id,nombre,email,rol FROM usuarios")
        data = cursor.fetchall()

    conn.close()

    return data


@app.delete("/usuarios/{id}", tags=["Usuarios"], summary="Eliminar usuario", description="Solo admin")
def delete_user(
    id: int,
    request: Request,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None)
):
    if request.state.rol != "admin":
        raise HTTPException(403, "Solo admin")

    conn = get_connection()

    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM usuarios WHERE id=%s", (id,))

    conn.commit()
    conn.close()

    return {"mensaje": "Usuario eliminado correctamente"}

# ======================
# PERFIL USUARIO ACTUAL
# ======================
@app.get("/me", tags=["Usuarios"], summary="Obtener usuario actual", description="Devuelve información del usuario autenticado")
def get_me(
    request: Request,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None)
):
    conn = get_connection()

    with conn.cursor() as cursor:
        cursor.execute("SELECT id,nombre,email,rol FROM usuarios WHERE id=%s", (request.state.user_id,))
        user = cursor.fetchone()

    conn.close()

    return user

# ======================
# STATS DASHBOARD
# ======================
@app.get("/stats", tags=["Dashboard"], summary="Estadísticas del sistema", description="admin: globales, user: personales")
def stats(
    request: Request,
    x_user_id: Optional[str] = Header(None),
    x_rol: Optional[str] = Header(None)
):
    user_id = request.state.user_id
    rol = request.state.rol

    conn = get_connection()
    with conn.cursor() as cursor:
        if rol == "admin":
            cursor.execute("SELECT COUNT(*) total FROM metas")
        else:
            cursor.execute("SELECT COUNT(*) total FROM metas WHERE usuario_id=%s", (user_id,))

        total = cursor.fetchone()["total"]

    conn.close()

    return {"total_metas": total}