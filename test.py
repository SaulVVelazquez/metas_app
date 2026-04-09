import pymysql

try:
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="",  # tu contraseña
        database="metas_app"
    )
    print("Conexión exitosa 🚀")
    conn.close()
except Exception as e:
    print("Error:", e)