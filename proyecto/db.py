import os
import sqlite3

URL_BD = os.environ.get("DATABASE_URL", "").strip()
USA_POSTGRES = bool(URL_BD)
RUTA_SQLITE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "usuarios.db")

if USA_POSTGRES:
    import psycopg
    from psycopg.rows import dict_row

    ErrorIntegridad = psycopg.IntegrityError
    ESQUEMA = """
    CREATE TABLE IF NOT EXISTS usuarios (
        id SERIAL PRIMARY KEY,
        correo TEXT NOT NULL UNIQUE,
        usuario TEXT NOT NULL UNIQUE,
        contrasena TEXT NOT NULL
    )
    """
else:
    ErrorIntegridad = sqlite3.IntegrityError
    ESQUEMA = """
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        correo TEXT NOT NULL UNIQUE,
        usuario TEXT NOT NULL UNIQUE,
        contrasena TEXT NOT NULL
    )
    """


class Conexion:

    def __init__(self, conexion):
        self.conexion = conexion

    def ejecutar(self, consulta, parametros=()):
        if USA_POSTGRES:
            consulta = consulta.replace("?", "%s")
        return self.conexion.execute(consulta, parametros)

    def __enter__(self):
        return self

    def __exit__(self, tipo, valor, rastro):
        try:
            if tipo is None:
                self.conexion.commit()
            else:
                self.conexion.rollback()
        finally:
            self.conexion.close()
        return False


def conectar():
    if USA_POSTGRES:
        return Conexion(psycopg.connect(URL_BD, row_factory=dict_row))
    conexion = sqlite3.connect(RUTA_SQLITE)
    conexion.row_factory = sqlite3.Row
    return Conexion(conexion)


def crear_tablas():
    with conectar() as db:
        db.ejecutar(ESQUEMA)


def buscar_usuario(usuario):
    with conectar() as db:
        return db.ejecutar(
            "SELECT id, usuario, correo, contrasena FROM usuarios WHERE usuario = ?",
            (usuario,),
        ).fetchone()


def buscar_correo(correo):
    with conectar() as db:
        return db.ejecutar(
            "SELECT id FROM usuarios WHERE correo = ?", (correo,)
        ).fetchone()


def crear_usuario(correo, usuario, contrasena_hash):
    with conectar() as db:
        db.ejecutar(
            "INSERT INTO usuarios (correo, usuario, contrasena) VALUES (?, ?, ?)",
            (correo, usuario, contrasena_hash),
        )
