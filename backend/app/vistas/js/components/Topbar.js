import { SessionStore } from "../state/SessionStore.js";
import { Formatter } from "../utils/Formatter.js";
import { ComponentBase } from "./ComponentBase.js";
import { Icon } from "./Icon.js";

export class Topbar extends ComponentBase {
  // props: { titulo, authService, sessionStore = SessionStore, onAlternarSidebar? }
  render() {
    const sessionStore = this.props.sessionStore || SessionStore;
    const usuario = sessionStore.obtenerUsuario();

    this.contenedor.innerHTML = "";
    this.contenedor.className = "topbar";

    if (typeof this.props.onAlternarSidebar === "function") {
      const botonMenu = document.createElement("button");
      botonMenu.type = "button";
      botonMenu.className = "topbar-boton-menu";
      botonMenu.appendChild(Icon.elemento("menu", { tamano: 20 }));
      this._escuchar(botonMenu, "click", this.props.onAlternarSidebar);
      this.contenedor.appendChild(botonMenu);
    }

    const titulo = document.createElement("h1");
    titulo.className = "topbar-titulo";
    titulo.textContent = this.props.titulo || "";
    this.contenedor.appendChild(titulo);

    const zonaDerecha = document.createElement("div");
    zonaDerecha.className = "topbar-zona-derecha";

    this._contenedorCampana = document.createElement("span");
    this._contenedorCampana.className = "topbar-campana";
    zonaDerecha.appendChild(this._contenedorCampana);

    const menuUsuario = document.createElement("div");
    menuUsuario.className = "topbar-usuario";

    const avatar = document.createElement("span");
    avatar.className = "avatar";
    avatar.textContent = usuario ? Formatter.iniciales(usuario.nombre, usuario.apellido) : "?";
    menuUsuario.appendChild(avatar);

    const infoUsuario = document.createElement("div");
    infoUsuario.className = "topbar-usuario-info";
    const nombre = document.createElement("span");
    nombre.className = "topbar-usuario-nombre";
    nombre.textContent = usuario ? usuario.nombreCompleto : "";
    infoUsuario.appendChild(nombre);
    const rol = document.createElement("span");
    rol.className = "topbar-usuario-rol";
    rol.textContent = usuario ? usuario.rol : "";
    infoUsuario.appendChild(rol);
    menuUsuario.appendChild(infoUsuario);

    const botonSalir = document.createElement("button");
    botonSalir.type = "button";
    botonSalir.className = "topbar-boton-salir";
    botonSalir.title = "Cerrar sesion";
    botonSalir.appendChild(Icon.elemento("salir", { tamano: 18 }));
    this._escuchar(botonSalir, "click", () => this._cerrarSesion());
    menuUsuario.appendChild(botonSalir);

    zonaDerecha.appendChild(menuUsuario);
    this.contenedor.appendChild(zonaDerecha);
  }

  obtenerContenedorCampana() {
    return this._contenedorCampana;
  }

  async _cerrarSesion() {
    const authService = this.props.authService;
    if (authService) {
      await authService.logout();
    }
    window.location.href = "login.html";
  }
}
