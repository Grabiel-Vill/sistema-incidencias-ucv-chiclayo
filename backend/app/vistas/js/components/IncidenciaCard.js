import { Formatter } from "../utils/Formatter.js";
import { ComponentBase } from "./ComponentBase.js";
import { Icon } from "./Icon.js";
import { StatusBadge } from "./StatusBadge.js";

export class IncidenciaCard extends ComponentBase {
  // props: { incidencia: IncidenciaRespuestaDTO, alHacerClick?(incidencia) }
  render() {
    const { incidencia, alHacerClick } = this.props;

    this.contenedor.innerHTML = "";
    this.contenedor.className = "tarjeta-incidencia";

    const encabezado = document.createElement("div");
    encabezado.className = "tarjeta-incidencia-encabezado";

    const ticket = document.createElement("div");
    ticket.className = "tarjeta-incidencia-ticket";
    ticket.appendChild(Icon.elemento("ticket", { tamano: 15, color: "var(--gris-400)" }));
    const codigo = document.createElement("span");
    codigo.textContent = incidencia.codigoTicket;
    ticket.appendChild(codigo);
    encabezado.appendChild(ticket);
    this.contenedor.appendChild(encabezado);

    const descripcion = document.createElement("p");
    descripcion.className = "tarjeta-incidencia-descripcion";
    descripcion.textContent = incidencia.descripcion;
    this.contenedor.appendChild(descripcion);

    const badges = document.createElement("div");
    badges.className = "tarjeta-incidencia-badges";
    this.contenedor.appendChild(badges);

    const espacioEstado = document.createElement("span");
    badges.appendChild(espacioEstado);
    this._badgeEstado = new StatusBadge(espacioEstado, { valor: incidencia.estado, tipo: "estado" });

    const espacioPrioridad = document.createElement("span");
    badges.appendChild(espacioPrioridad);
    this._badgePrioridad = new StatusBadge(espacioPrioridad, { valor: incidencia.prioridad, tipo: "prioridad" });

    const pie = document.createElement("div");
    pie.className = "tarjeta-incidencia-pie";

    const tecnico = document.createElement("span");
    tecnico.textContent = incidencia.tecnicoAsignado ? `Tecnico: ${incidencia.tecnicoAsignado}` : "Sin tecnico asignado";
    pie.appendChild(tecnico);

    const fecha = document.createElement("small");
    fecha.textContent = Formatter.fechaLegible(incidencia.fechaCreacion);
    pie.appendChild(fecha);

    this.contenedor.appendChild(pie);

    if (typeof alHacerClick === "function") {
      this.contenedor.classList.add("tarjeta-incidencia-clicable");
      this._escuchar(this.contenedor, "click", () => alHacerClick(incidencia));
    }
  }

  destruir() {
    this._badgeEstado?.destruir();
    this._badgePrioridad?.destruir();
    super.destruir();
  }
}
