import { Icon } from "../components/Icon.js";
import { Toast } from "../components/Toast.js";
import { API_BASE_URL } from "../config.js";
import { CredencialesDTO } from "../models/CredencialesDTO.js";
import { AuthService } from "../services/AuthService.js";
import { SessionStore } from "../state/SessionStore.js";
import { ApiException } from "../utils/ApiException.js";
import { HttpClient } from "../utils/HttpClient.js";
import { Validators } from "../utils/Validators.js";

const DESTINO_POR_ROL = {
  DOCENTE: "docente-panel.html",
  TECNICO: "tecnico-bandeja.html",
  ADMINISTRADOR: "admin-dashboard.html",
};

export class LoginController {
  constructor(contenedor) {
    this.contenedor = contenedor;
    this.http = new HttpClient(API_BASE_URL);
    this.authService = new AuthService(this.http);

    if (SessionStore.estaAutenticado()) {
      window.location.href = DESTINO_POR_ROL[SessionStore.obtenerUsuario().rol] || "login.html";
      return;
    }
    this._render();
  }

  // ---------- Render ----------

  _render() {
    this.contenedor.innerHTML = "";

    this.encabezado = document.createElement("div");
    this.encabezado.className = "login-encabezado";
    const h1 = document.createElement("h1");
    h1.textContent = "Inicia sesión en tu cuenta";
    this.encabezado.append(h1);
    this.contenedor.appendChild(this.encabezado);

    this.formulario = document.createElement("form");
    this.formulario.className = "formulario-login";
    this.formulario.noValidate = true;
    this.formulario.addEventListener("submit", (e) => {
      e.preventDefault();
      this._enviar();
    });
    this.contenedor.appendChild(this.formulario);

    this.campos = {};
    this.formulario.appendChild(
      this._campo("email", "Correo institucional", "email", "nombre@ucvvirtual.edu.pe", "correo", {
        autocomplete: "username",
      }),
    );
    this.formulario.appendChild(
      this._campo("password", "Contraseña", "password", "Tu contraseña", "candado", {
        autocomplete: "current-password",
        verContrasena: true,
      }),
    );

    this.areaError = document.createElement("p");
    this.areaError.className = "mensaje-error";
    this.areaError.setAttribute("role", "alert");
    this.formulario.appendChild(this.areaError);

    this.boton = document.createElement("button");
    this.boton.type = "submit";
    this.boton.className = "boton boton-primario login-boton";
    this._textoBoton("Ingresar");
    this.formulario.appendChild(this.boton);

    const primero = Object.values(this.campos)[0];
    if (primero) primero.input.focus();
  }

  _campo(clave, etiqueta, tipo, placeholder, icono, { autocomplete, verContrasena = false } = {}) {
    const grupo = document.createElement("div");
    grupo.className = "campo-formulario";

    const id = `login-${clave}`;
    const label = document.createElement("label");
    label.htmlFor = id;
    label.textContent = etiqueta;
    grupo.appendChild(label);

    const caja = document.createElement("div");
    caja.className = "login-caja";
    const ic = Icon.elemento(icono, { tamano: 17 });
    ic.classList.add("login-caja-icono");
    caja.appendChild(ic);

    const input = document.createElement("input");
    input.id = id;
    input.type = tipo;
    input.placeholder = placeholder;
    input.autocomplete = autocomplete || "off";
    input.addEventListener("input", () => this._limpiarError(clave));
    caja.appendChild(input);

    if (verContrasena) {
      const ojo = document.createElement("button");
      ojo.type = "button";
      ojo.className = "login-ojo";
      ojo.setAttribute("aria-label", "Mostrar contraseña");
      ojo.setAttribute("aria-pressed", "false");
      ojo.innerHTML = Icon.elemento("ojo", { tamano: 18 }).innerHTML;
      ojo.addEventListener("click", () => {
        const visible = input.type === "password";
        input.type = visible ? "text" : "password";
        ojo.setAttribute("aria-pressed", String(visible));
        ojo.setAttribute("aria-label", visible ? "Ocultar contraseña" : "Mostrar contraseña");
        ojo.innerHTML = Icon.elemento(visible ? "ojoOculto" : "ojo", { tamano: 18 }).innerHTML;
        input.focus();
      });
      caja.appendChild(ojo);
    }
    grupo.appendChild(caja);

    const aviso = document.createElement("small");
    aviso.className = "login-aviso";
    grupo.appendChild(aviso);

    if (tipo === "password") {
      input.addEventListener("keyup", (e) => {
        const mayus = e.getModifierState && e.getModifierState("CapsLock");
        aviso.classList.remove("error");
        aviso.textContent = mayus ? "Tienes las mayúsculas activadas" : "";
      });
    }

    this.campos[clave] = { grupo, input, aviso };
    return grupo;
  }

  // ---------- Validación ----------

  _marcarError(clave, mensaje) {
    const campo = this.campos[clave];
    if (!campo) return;
    campo.grupo.classList.add("con-error");
    campo.aviso.classList.add("error");
    campo.aviso.textContent = mensaje;
  }

  _limpiarError(clave) {
    const campo = this.campos[clave];
    if (!campo) return;
    campo.grupo.classList.remove("con-error");
    campo.aviso.classList.remove("error");
    campo.aviso.textContent = "";
    this.areaError.textContent = "";
  }

  _valor(clave) {
    return this.campos[clave] ? this.campos[clave].input.value : "";
  }

  _validar() {
    const errores = {};
    if (!Validators.esEmailValido(this._valor("email"))) {
      errores.email = "Escribe un correo válido, por ejemplo nombre@ucvvirtual.edu.pe";
    }
    if (!Validators.esNoVacio(this._valor("password"))) {
      errores.password = "Ingresa tu contraseña";
    }
    return errores;
  }

  // ---------- Envío ----------

  _textoBoton(texto, cargando = false) {
    this.boton.innerHTML = "";
    if (cargando) {
      const spinner = document.createElement("span");
      spinner.className = "login-spinner";
      this.boton.appendChild(spinner);
    }
    this.boton.append(texto);
  }

  async _enviar() {
    this.areaError.textContent = "";
    const errores = this._validar();
    const claves = Object.keys(errores);
    for (const k of Object.keys(this.campos)) this._limpiarError(k);
    if (claves.length > 0) {
      claves.forEach((k) => this._marcarError(k, errores[k]));
      this.campos[claves[0]].input.focus();
      return;
    }

    this.boton.disabled = true;
    this._textoBoton("Ingresando…", true);
    try {
      const token = await this.authService.login(new CredencialesDTO(this._valor("email"), this._valor("password")));
      window.location.href = DESTINO_POR_ROL[token.rol] || "login.html";
    } catch (error) {
      const mensaje = error instanceof ApiException ? error.message : "No pudimos conectar con el servidor. Intenta de nuevo.";
      this.areaError.textContent = mensaje;
      Toast.error(mensaje);
      this.boton.disabled = false;
      this._textoBoton("Ingresar");
    }
  }
}
