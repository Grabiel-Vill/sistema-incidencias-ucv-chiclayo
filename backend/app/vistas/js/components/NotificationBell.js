import { Formatter } from "../utils/Formatter.js";
import { ComponentBase } from "./ComponentBase.js";
import { Icon } from "./Icon.js";
import { Toast } from "./Toast.js";

export class NotificationBell extends ComponentBase {
  // props: { notificationStore }
  render() {
    this.contenedor.innerHTML = "";
    this.contenedor.className = "campana-notificaciones";
    this._idsAlertados = new Set();

    this._boton = document.createElement("button");
    this._boton.type = "button";
    this._boton.className = "campana-boton";
    this._boton.appendChild(Icon.elemento("campana", { tamano: 19 }));
    this._contador = document.createElement("span");
    this._contador.className = "campana-contador campana-contador-oculto";
    this._boton.appendChild(this._contador);
    this.contenedor.appendChild(this._boton);

    this._lista = document.createElement("div");
    this._lista.className = "campana-lista campana-lista-oculta";
    this.contenedor.appendChild(this._lista);

    this._escuchar(this._boton, "click", () => this._alternarLista());
    this._escuchar(document, "click", (evento) => {
      if (!this.contenedor.contains(evento.target)) {
        this._lista.classList.add("campana-lista-oculta");
      }
    });

    const store = this.props.notificationStore;
    if (store) {
      this._desuscribir = store.suscribir((notificaciones) => this._pintar(notificaciones));
      this._pintar(store.listar());
      store.cargar().catch(() => {});
    } else {
      this._pintar([]);
    }
  }

  destruir() {
    if (this._desuscribir) {
      this._desuscribir();
      this._desuscribir = null;
    }
    super.destruir();
  }

  _alternarLista() {
    this._lista.classList.toggle("campana-lista-oculta");
  }

  _pintar(notificaciones) {
    const noLeidas = notificaciones.filter((notificacion) => !notificacion.leido).length;
    this._contador.textContent = noLeidas > 9 ? "9+" : String(noLeidas);
    this._contador.classList.toggle("campana-contador-oculto", noLeidas === 0);

    const nuevasAlta = notificaciones.filter(
      (n) => !n.leido && n.prioridad === "ALTA" && n.tipo === "ASIGNACION" && !this._idsAlertados.has(n.idNotificacion),
    );
    for (const notificacion of nuevasAlta) {
      this._idsAlertados.add(notificacion.idNotificacion);
      Toast.error(`Prioridad ALTA: ${notificacion.mensaje}`);
    }

    this._lista.innerHTML = "";

    const encabezado = document.createElement("div");
    encabezado.className = "campana-lista-encabezado";
    encabezado.textContent = "Notificaciones";
    this._lista.appendChild(encabezado);

    if (notificaciones.length === 0) {
      const vacio = document.createElement("p");
      vacio.className = "campana-vacio";
      vacio.textContent = "No tienes notificaciones";
      this._lista.appendChild(vacio);
      return;
    }

    const contenedorItems = document.createElement("ul");
    for (const notificacion of notificaciones) {
      const item = document.createElement("li");
      item.className = notificacion.leido ? "campana-item-leido" : "campana-item-no-leido";
      const esAltaAsignacion = notificacion.prioridad === "ALTA" && notificacion.tipo === "ASIGNACION";
      item.classList.toggle("campana-item-alta", esAltaAsignacion);

      const mensaje = document.createElement("p");
      if (esAltaAsignacion) {
        const etiqueta = document.createElement("span");
        etiqueta.className = "campana-etiqueta-alta";
        etiqueta.textContent = "ALTA";
        mensaje.appendChild(etiqueta);
      }
      mensaje.appendChild(document.createTextNode(notificacion.mensaje));
      item.appendChild(mensaje);

      const fecha = document.createElement("small");
      fecha.textContent = Formatter.fechaLegible(notificacion.fecha);
      item.appendChild(fecha);

      item.addEventListener("click", () => {
        if (!notificacion.leido) {
          this.props.notificationStore.marcarLeido(notificacion.idNotificacion);
        }
      });
      contenedorItems.appendChild(item);
    }
    this._lista.appendChild(contenedorItems);
  }
}
