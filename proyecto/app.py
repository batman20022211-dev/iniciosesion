import os
import re

from flask import Flask, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from db import (
    ErrorIntegridad,
    buscar_correo,
    buscar_usuario,
    crear_tablas,
    crear_usuario,
)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "cambia-esta-clave-en-produccion")

REGEX_CORREO = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")

crear_tablas()


def validar_registro(correo, usuario, contrasena, confirmar):
    if not REGEX_CORREO.match(correo):
        return "Escribe un correo válido."
    if len(usuario) < 3:
        return "El usuario debe tener al menos 3 caracteres."
    if len(contrasena) < 6:
        return "La contraseña debe tener mínimo 6 caracteres."
    if contrasena != confirmar:
        return "Las contraseñas no coinciden."
    if buscar_usuario(usuario):
        return "Ese usuario ya existe. Elige otro."
    if buscar_correo(correo):
        return "Ese correo ya está registrado."
    return None


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip()
        contrasena = request.form.get("contrasena", "")

        if not usuario or not contrasena:
            return render_template(
                "login.html", error="Escribe tu usuario y contraseña.", usuario=usuario
            )

        fila = buscar_usuario(usuario)
        if fila is None:
            flash("No tienes cuenta todavía. Regístrate para continuar.", "aviso")
            return redirect(url_for("registro", usuario=usuario))

        if not check_password_hash(fila["contrasena"], contrasena):
            return render_template(
                "login.html", error="Contraseña incorrecta.", usuario=usuario
            )

        session["usuario"] = fila["usuario"]
        return redirect(url_for("hola"))

    return render_template("login.html")


@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        correo = request.form.get("correo", "").strip().lower()
        usuario = request.form.get("usuario", "").strip()
        contrasena = request.form.get("contrasena", "")
        confirmar = request.form.get("confirmar", "")

        error = validar_registro(correo, usuario, contrasena, confirmar)
        if error:
            return render_template(
                "registro.html",
                error=error,
                valores={"correo": correo, "usuario": usuario},
            )

        try:
            crear_usuario(correo, usuario, generate_password_hash(contrasena))
        except ErrorIntegridad:
            return render_template(
                "registro.html",
                error="Ese usuario o correo ya existe.",
                valores={"correo": correo, "usuario": usuario},
            )

        flash("Cuenta creada. Ya puedes iniciar sesión.", "exito")
        return redirect(url_for("login"))

    valores = {
        "correo": "",
        "usuario": request.args.get("usuario", "").strip(),
    }
    return render_template("registro.html", valores=valores)


@app.route("/hola")
def hola():
    if "usuario" not in session:
        return redirect(url_for("login"))
    return render_template("hola.html", usuario=session["usuario"])


@app.route("/salir")
def salir():
    session.clear()
    flash("Sesión cerrada.", "aviso")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
