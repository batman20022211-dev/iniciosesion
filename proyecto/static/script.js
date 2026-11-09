document.addEventListener("DOMContentLoaded", () => {
    const REGEX_CORREO = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    const formLogin = document.getElementById("form-login");
    const formRegistro = document.getElementById("form-registro");

    // Cada validador recibe el valor del campo y regresa un mensaje de error ("" si está bien).
    const validadores = {
        "usuario": (v) => v.trim() ? "" : "Escribe tu usuario.",
        "contrasena": (v) => v ? "" : "Escribe tu contraseña.",
        "reg-correo": (v) => REGEX_CORREO.test(v.trim()) ? "" : "Escribe un correo válido.",
        "reg-usuario": (v) => v.trim().length >= 3 ? "" : "El usuario debe tener al menos 3 caracteres.",
        "reg-contrasena": (v) => v.length >= 6 ? "" : "La contraseña debe tener mínimo 6 caracteres.",
        "reg-confirmar": (v) => v === document.getElementById("reg-contrasena").value
            ? "" : "Las contraseñas no coinciden.",
    };

    function marcarCampo(campo, mensajeError) {
        const aviso = campo.closest(".grupo").querySelector(".mensaje-campo");
        if (mensajeError) {
            campo.classList.add("invalido");
            aviso.textContent = mensajeError;
            return false;
        }
        campo.classList.remove("invalido");
        aviso.textContent = "";
        return true;
    }

    function validarCampo(campo) {
        const validador = validadores[campo.id];
        if (!validador) return true;
        return marcarCampo(campo, validador(campo.value));
    }

    function validarFormulario(ids) {
        // map (no some/every directo) para que se marquen todos los errores a la vez
        return ids
            .map((id) => validarCampo(document.getElementById(id)))
            .every(Boolean);
    }

    if (formLogin) {
        formLogin.addEventListener("submit", (evento) => {
            if (!validarFormulario(["usuario", "contrasena"])) {
                evento.preventDefault();
            }
        });
    }

    if (formRegistro) {
        formRegistro.addEventListener("submit", (evento) => {
            const ids = ["reg-correo", "reg-usuario", "reg-contrasena", "reg-confirmar"];
            if (!validarFormulario(ids)) {
                evento.preventDefault();
            }
        });
    }

    // Validación mientras escribe: al salir del campo, y después de error si ya lo corrigió
    document.querySelectorAll("#form-login input, #form-registro input").forEach((campo) => {
        campo.addEventListener("blur", () => validarCampo(campo));
        campo.addEventListener("input", () => {
            if (campo.classList.contains("invalido")) validarCampo(campo);
        });
    });
});
