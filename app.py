from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
import pymysql

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
# MODELOS
# ======================
class Mensaje(BaseModel):
    mensaje: str

class Meta(BaseModel):
    id: int
    usuario_id: int
    categoria_id: Optional[int]
    titulo: str
    descripcion: Optional[str]
    progreso: int
    estado: str
    fecha_inicio: Optional[str]
    fecha_limite: Optional[str]

class MetaIN(BaseModel):
    usuario_id: int
    categoria_id: Optional[int]
    titulo: str
    descripcion: Optional[str] = None
    progreso: int = Field(ge=0, le=100)
    estado: str
    fecha_inicio: Optional[str] = None
    fecha_limite: Optional[str] = None

class MetaUpdate(BaseModel):
    titulo: Optional[str] = None
    descripcion: Optional[str] = None
    progreso: Optional[int] = Field(default=None, ge=0, le=100)
    estado: Optional[str] = None

# ======================
# APP
# ======================
app = FastAPI(
    title="Metas API",
    description="API sencilla para manejar metas personales pruebas",
    version="1.0"
)
origins = [
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======================
# ROOT
# ======================
@app.get("/")
def home():
    return {"mensaje": "API funcionando"}

# ======================
# GET TODAS
# ======================
@app.get("/metas", response_model=List[Meta])
def get_metas():
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM metas")
        data = cursor.fetchall()
    conn.close()
    return data

# ======================
# GET POR ID
# ======================
@app.get("/metas/{id}", response_model=Meta)
def get_meta(id: int):
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM metas WHERE id=%s", (id,))
        data = cursor.fetchone()
    conn.close()

    if not data:
        return JSONResponse(status_code=404, content={"mensaje": "Meta no encontrada"})

    return data

# ======================
# GET POR USUARIO
# ======================
@app.get("/metas/usuario/{usuario_id}", response_model=List[Meta])
def get_metas_usuario(usuario_id: int):
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM metas WHERE usuario_id=%s", (usuario_id,))
        data = cursor.fetchall()
    conn.close()
    return data

# ======================
# JOIN DETALLE
# ======================
@app.get("/metas-detalle")
def get_metas_detalle():
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
        SELECT m.id, m.titulo, m.progreso,
               u.nombre AS usuario,
               c.nombre AS categoria
        FROM metas m
        JOIN usuarios u ON m.usuario_id = u.id
        LEFT JOIN categorias c ON m.categoria_id = c.id
        """)
        data = cursor.fetchall()
    conn.close()
    return data

# ======================
# POST
# ======================
@app.post("/metas", response_model=Mensaje)
def create_meta(meta: MetaIN):

    estado = meta.estado
    if meta.progreso == 100:
        estado = "completado"

    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
        INSERT INTO metas
        (usuario_id,categoria_id,titulo,descripcion,progreso,estado,fecha_inicio,fecha_limite)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """,(
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
    return {"mensaje":"Meta creada"}

# ======================
# PUT (REEMPLAZO TOTAL)
# ======================
@app.put("/metas/{id}", response_model=Mensaje)
def replace_meta(id: int, meta: MetaIN):

    conn = get_connection()
    with conn.cursor() as cursor:

        cursor.execute("SELECT * FROM metas WHERE id=%s",(id,))
        if not cursor.fetchone():
            conn.close()
            return JSONResponse(status_code=404,content={"mensaje":"No existe"})

        estado = meta.estado
        if meta.progreso == 100:
            estado = "completado"

        cursor.execute("""
        UPDATE metas
        SET usuario_id=%s,
            categoria_id=%s,
            titulo=%s,
            descripcion=%s,
            progreso=%s,
            estado=%s,
            fecha_inicio=%s,
            fecha_limite=%s
        WHERE id=%s
        """,(
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
    return {"mensaje":"Meta reemplazada"}

# ======================
# PATCH
# ======================
@app.patch("/metas/{id}", response_model=Mensaje)
def update_meta(id: int, meta: MetaUpdate):

    conn = get_connection()
    with conn.cursor() as cursor:

        cursor.execute("SELECT * FROM metas WHERE id=%s",(id,))
        existing = cursor.fetchone()

        if not existing:
            conn.close()
            return JSONResponse(status_code=404,content={"mensaje":"No existe"})

        update_data = meta.dict(exclude_unset=True)

        if "progreso" in update_data and update_data["progreso"] == 100:
            update_data["estado"] = "completado"

        fields = []
        values = []

        for k,v in update_data.items():
            fields.append(f"{k}=%s")
            values.append(v)

        if not fields:
            conn.close()
            return {"mensaje":"Nada que actualizar"}

        values.append(id)

        sql = f"UPDATE metas SET {', '.join(fields)} WHERE id=%s"
        cursor.execute(sql, tuple(values))

    conn.commit()
    conn.close()
    return {"mensaje":"Actualizada parcialmente"}

# ======================
# DELETE
# ======================
@app.delete("/metas/{id}", response_model=Mensaje)
def delete_meta(id: int):

    conn = get_connection()
    with conn.cursor() as cursor:

        cursor.execute("SELECT id FROM metas WHERE id=%s",(id,))
        if not cursor.fetchone():
            conn.close()
            return JSONResponse(status_code=404,content={"mensaje":"No existe"})

        cursor.execute("DELETE FROM metas WHERE id=%s",(id,))

    conn.commit()
    conn.close()
    return {"mensaje":"Eliminada"}
@app.post("/login")
def login(email: str, password: str):

    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT id, nombre, rol FROM usuarios WHERE email=%s AND password=%s",
            (email, password)
        )
        user = cursor.fetchone()

    conn.close()

    if not user:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    return {
        "mensaje": "Login correcto",
        "usuario": user
    }