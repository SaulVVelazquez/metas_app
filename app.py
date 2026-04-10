# 
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
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
        if not hashed:
            return False

        return bcrypt.checkpw(
            password.encode("utf-8"),
            hashed.encode("utf-8")
        )
    except Exception:
        return False


# ======================
# MODELOS
# ======================
class UsuarioIN(BaseModel):
    nombre: str
    email: str
    password: str
    rol: Literal["admin", "user"]

class Login(BaseModel):
    email: str
    password: str

class CategoriaIN(BaseModel):
    nombre: str

class MetaIN(BaseModel):
    usuario_id: int
    categoria_id: Optional[int]
    titulo: str
    descripcion: Optional[str] = None
    progreso: int = Field(ge=0, le=100)
    estado: Literal["pendiente", "en progreso", "completado"]
    fecha_inicio: Optional[str] = None
    fecha_limite: Optional[str] = None


# ======================
# APP
# ======================
app = FastAPI(
    title="API Metas",
    description="Sistema con roles (admin / user) usando headers",
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
# MIDDLEWARE (FIXED)
# ======================
@app.middleware("http")
async def auth(request: Request, call_next):

    #   permitir CORS preflight
    if request.method == "OPTIONS":
        return await call_next(request)

    rutas_publicas = [
        "/", "/login", "/register",
        "/docs", "/openapi.json"
    ]

    if request.url.path in rutas_publicas:
        return await call_next(request)

    user_id = request.headers.get("x-user-id")
    rol = request.headers.get("x-rol")

    # NO HTTPException en middleware
    if not user_id or not rol:
        return JSONResponse(
            status_code=401,
            content={"detail": "Falta autenticación"}
        )

    try:
        request.state.user_id = int(user_id)
    except:
        return JSONResponse(
            status_code=401,
            content={"detail": "user_id inválido"}
        )

    request.state.rol = rol

    return await call_next(request)


# ======================
# ROOT
# ======================
@app.get("/")
def home():
    return {"mensaje": "API funcionando"}


# ======================
# AUTH
# ======================
@app.post("/register")
def register(user: UsuarioIN):

    conn = get_connection()
    with conn.cursor() as cursor:

        cursor.execute("SELECT id FROM usuarios WHERE email=%s", (user.email,))
        if cursor.fetchone():
            raise HTTPException(400, "Email ya registrado")

        hashed = hash_password(user.password)

        cursor.execute("""
            INSERT INTO usuarios (nombre, email, password, rol)
            VALUES (%s,%s,%s,%s)
        """, (user.nombre, user.email, hashed, user.rol))

        conn.commit()

    conn.close()
    return {"mensaje": "Usuario creado"}


@app.post("/login")
def login(data: Login):

    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM usuarios WHERE email=%s", (data.email,))
        user = cursor.fetchone()

    conn.close()

    if not user:
        raise HTTPException(401, "Credenciales incorrectas")

    if not verify_password(data.password, user.get("password", "")):
        raise HTTPException(401, "Credenciales incorrectas")

    return {
        "mensaje": "Login correcto",
        "x-user-id": user["id"],
        "x-rol": user["rol"],
        "nombre": user["nombre"]
    }


# ======================
# CATEGORIAS
# ======================
@app.get("/categorias")
def get_categorias():

    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM categorias")
        data = cursor.fetchall()

    conn.close()
    return data


@app.post("/categorias")
def create_categoria(cat: CategoriaIN, request: Request):

    if request.state.rol != "admin":
        raise HTTPException(403, "Solo admin")

    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            "INSERT INTO categorias (nombre) VALUES (%s)",
            (cat.nombre,)
        )

    conn.commit()
    conn.close()
    return {"mensaje": "Categoría creada"}


# ======================
# USUARIOS
# ======================
@app.get("/usuarios")
def get_usuarios(request: Request):

    if request.state.rol != "admin":
        raise HTTPException(403, "Solo admin")

    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT id,nombre,email,rol FROM usuarios")
        data = cursor.fetchall()

    conn.close()
    return data


@app.delete("/usuarios/{id}")
def delete_usuario(id: int, request: Request):

    if request.state.rol != "admin":
        raise HTTPException(403, "Solo admin")

    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM usuarios WHERE id=%s", (id,))

    conn.commit()
    conn.close()
    return {"mensaje": "Usuario eliminado"}


# ======================
# METAS
# ======================
@app.get("/metas")
def get_metas(request: Request):

    user_id = request.state.user_id
    rol = request.state.rol

    conn = get_connection()
    with conn.cursor() as cursor:

        if rol == "admin":
            cursor.execute("SELECT * FROM metas")
        else:
            cursor.execute(
                "SELECT * FROM metas WHERE usuario_id=%s",
                (user_id,)
            )

        data = cursor.fetchall()

    conn.close()
    return data


@app.post("/metas")
def create_meta(meta: MetaIN, request: Request):

    estado = meta.estado
    if meta.progreso == 100:
        estado = "completado"

    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            INSERT INTO metas
            (usuario_id,categoria_id,titulo,descripcion,progreso,estado,fecha_inicio,fecha_limite)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            meta.usuario_id,
            meta.categoria_id,
            meta.titulo,
            meta.descripcion,
            meta.progreso,
            estado,
            meta.fecha_inicio,
            meta.fecha_limite
        ))

    conn.commit()
    conn.close()
    return {"mensaje": "Meta creada"}


@app.put("/metas/{id}")
def update_meta(id: int, meta: MetaIN, request: Request):

    user_id = request.state.user_id
    rol = request.state.rol

    conn = get_connection()
    with conn.cursor() as cursor:

        cursor.execute("SELECT * FROM metas WHERE id=%s", (id,))
        existing = cursor.fetchone()

        if not existing:
            raise HTTPException(404, "No existe")

        if rol != "admin" and existing["usuario_id"] != user_id:
            raise HTTPException(403, "No autorizado")

        estado = meta.estado
        if meta.progreso == 100:
            estado = "completado"

        cursor.execute("""
            UPDATE metas SET
            usuario_id=%s,
            categoria_id=%s,
            titulo=%s,
            descripcion=%s,
            progreso=%s,
            estado=%s,
            fecha_inicio=%s,
            fecha_limite=%s
            WHERE id=%s
        """, (
            meta.usuario_id,
            meta.categoria_id,
            meta.titulo,
            meta.descripcion,
            meta.progreso,
            estado,
            meta.fecha_inicio,
            meta.fecha_limite,
            id
        ))

    conn.commit()
    conn.close()
    return {"mensaje": "Actualizada"}


@app.delete("/metas/{id}")
def delete_meta(id: int, request: Request):

    user_id = request.state.user_id
    rol = request.state.rol

    conn = get_connection()
    with conn.cursor() as cursor:

        cursor.execute("SELECT * FROM metas WHERE id=%s", (id,))
        meta = cursor.fetchone()

        if not meta:
            raise HTTPException(404, "No existe")

        if rol != "admin" and meta["usuario_id"] != user_id:
            raise HTTPException(403, "No autorizado")

        cursor.execute("DELETE FROM metas WHERE id=%s", (id,))

    conn.commit()
    conn.close()
    return {"mensaje": "Eliminada"}