import { NotificationBell } from "../components/NotificationBell.js";
import { Sidebar } from "../components/Sidebar.js";
import { Topbar } from "../components/Topbar.js";
import { API_BASE_URL } from "../config.js";
import { AuthService } from "../services/AuthService.js";
import { NotificacionService } from "../services/NotificacionService.js";
import { NotificationStore } from "../state/NotificationStore.js";
import { SessionStore } from "../state/SessionStore.js";
import { HttpClient } from "../utils/HttpClient.js";

export class PageControllerBase {
  constructor(contenedor, rolesPermitidos = [], tituloPagina = "") {
    const autenticado = SessionStore.estaAutenticado();
    const autorizado = rolesPermitidos.length === 0 || SessionStore.tieneRol(...rolesPermitidos);
    if (!autenticado || !autorizado) {
      window.location.href = "login.html";
      return;
    }

    this.contenedor = contenedor;
    this.http = new HttpClient(API_BASE_URL);
    this.authService = new AuthService(this.http);
    this.notificacionService = new NotificacionService(this.http);
    this.notificationStore = new NotificationStore(this.notificacionService);

    this._montarShell(tituloPagina);
    this.inicializar();
  }

  inicializar() {
    throw new Error("inicializar() debe ser implementado por la subclase");
  }

  _montarShell(tituloPagina) {
    const contenedorSidebar = document.getElementById("contenedor-sidebar");
    if (contenedorSidebar) {
      this.sidebar = new Sidebar(contenedorSidebar);
    }

    const contenedorTopbar = document.getElementById("contenedor-topbar");
    if (contenedorTopbar) {
      this.topbar = new Topbar(contenedorTopbar, {
        titulo: tituloPagina,
        authService: this.authService,
        onAlternarSidebar: contenedorSidebar
          ? () => contenedorSidebar.classList.toggle("sidebar-abierta")
          : undefined,
      });

      const contenedorCampana = this.topbar.obtenerContenedorCampana();
      if (contenedorCampana) {
        this.notificationBell = new NotificationBell(contenedorCampana, {
          notificationStore: this.notificationStore,
        });
      }
    }
    this.notificationStore.iniciarPolling();
  }
}
