import { SessionStore } from "../state/SessionStore.js";
import { ComponentBase } from "./ComponentBase.js";
import { Icon } from "./Icon.js";

const MENU_POR_ROL = {
  DOCENTE: [{ texto: "Mi panel", href: "docente-panel.html", icono: "dashboard" }],
  TECNICO: [{ texto: "Bandeja tecnica", href: "tecnico-bandeja.html", icono: "bandeja" }],
  ADMINISTRADOR: [
    { texto: "Dashboard", href: "admin-dashboard.html", icono: "dashboard" },
    { texto: "Gestion de incidencias", href: "admin-incidencias.html", icono: "ticket" },
    { texto: "Usuarios", href: "admin-usuarios.html", icono: "usuarios" },
    { texto: "Laboratorios", href: "admin-laboratorios.html", icono: "laboratorio" },
    { texto: "Reportes", href: "admin-reportes.html", icono: "reportes" },
  ],
};

export class Sidebar extends ComponentBase {
  // props: { sessionStore = SessionStore }
  render() {
    const sessionStore = this.props.sessionStore || SessionStore;
    const usuario = sessionStore.obtenerUsuario();
    const items = (usuario && MENU_POR_ROL[usuario.rol]) || [];
    const paginaActual = typeof window !== "undefined" ? window.location.pathname.split("/").pop() : "";

    this.contenedor.innerHTML = "";
    this.contenedor.className = "sidebar";

    const marca = document.createElement("div");
    marca.className = "sidebar-marca";
    marca.appendChild(Icon.elemento("laboratorio", { tamano: 22, color: "var(--marca-500)" }));
    const marcaTexto = document.createElement("span");
    marcaTexto.textContent = "Incidencias UCV";
    marca.appendChild(marcaTexto);
    this.contenedor.appendChild(marca);

    const nav = document.createElement("nav");
    nav.className = "sidebar-nav";
    for (const item of items) {
      const enlace = document.createElement("a");
      enlace.href = item.href;
      enlace.className = "sidebar-enlace";
      if (item.href === paginaActual) {
        enlace.classList.add("sidebar-enlace-activo");
      }
      enlace.appendChild(Icon.elemento(item.icono, { tamano: 18 }));
      const texto = document.createElement("span");
      texto.textContent = item.texto;
      enlace.appendChild(texto);
      nav.appendChild(enlace);
    }
    this.contenedor.appendChild(nav);

    const pie = document.createElement("div");
    pie.className = "sidebar-pie";
    pie.textContent = "UCV Chiclayo";
    this.contenedor.appendChild(pie);
  }
}
