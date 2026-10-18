import { Formatter } from "../utils/Formatter.js";
import { ComponentBase } from "./ComponentBase.js";
import { EmptyState } from "./EmptyState.js";
import { StatusBadge } from "./StatusBadge.js";

const ESTADOS_SIGUIENTES = {
  RECIBIDO: "EN_PROCESO",
  PROGRAMADO: "EN_PROCESO",
  EN_PROCESO: "RESUELTO",
};

const ETIQUETAS_ESTADO = { EN_PROCESO: "en proceso", RESUELTO: "resuelto" };

export class IncidenciaTable extends ComponentBase {
  // props: { incidencias: IncidenciaRespuestaDTO[], onAtender?, onCambiarEstado?, onSeleccionar?,
  //   onCalificar?, etiquetasEstado?: override de etiquetas para StatusBadge (ver StatusBadge.js) }
  render() {
    const { incidencias = [] } = this.props;
    this._badges = [];

    this.contenedor.innerHTML = "";
    this.contenedor.className = "tabla-incidencias";

    if (incidencias.length === 0) {
      this._vacio = new EmptyState(this.contenedor.appendChild(document.createElement("div")), {
        icono: "ticket",
        titulo: "No hay incidencias para mostrar",
        descripcion: "Cuando se registre una incidencia aparecera aqui.",
      });
      return;
    }

    const envoltorio = document.createElement("div");
    envoltorio.className = "tabla-incidencias-envoltorio";

    const tabla = document.createElement("table");
    const encabezado = document.createElement("thead");
    encabezado.innerHTML = `
      <tr>
        <th>Ticket</th>
        <th>Descripcion</th>
        <th>Estado</th>
        <th>Prioridad</th>
        <th>Tecnico</th>
        <th>Creada</th>
        <th></th>
      </tr>
    `;
    tabla.appendChild(encabezado);

    const cuerpo = document.createElement("tbody");
    for (const incidencia of incidencias) {
      cuerpo.appendChild(this._crearFila(incidencia));
    }
    tabla.appendChild(cuerpo);

    envoltorio.appendChild(tabla);
    this.contenedor.appendChild(envoltorio);
  }

  destruir() {
    for (const badge of this._badges || []) {
      badge.destruir();
    }
    this._badges = [];
    this._vacio?.destruir();
    super.destruir();
  }

  _crearFila(incidencia) {
    const fila = document.createElement("tr");

    const celdaTicket = this._celda(incidencia.codigoTicket);
    celdaTicket.className = "celda-ticket";
    fila.appendChild(celdaTicket);

    const celdaDescripcion = this._celda(incidencia.descripcion);
    celdaDescripcion.className = "celda-descripcion";
    fila.appendChild(celdaDescripcion);

    const celdaEstado = document.createElement("td");
    const espacioEstado = document.createElement("span");
    celdaEstado.appendChild(espacioEstado);
    fila.appendChild(celdaEstado);
    this._badges.push(
      new StatusBadge(espacioEstado, {
        valor: incidencia.estado,
        tipo: "estado",
        etiquetas: this.props.etiquetasEstado || {},
      }),
    );

    const celdaPrioridad = document.createElement("td");
    const espacioPrioridad = document.createElement("span");
    celdaPrioridad.appendChild(espacioPrioridad);
    fila.appendChild(celdaPrioridad);
    this._badges.push(new StatusBadge(espacioPrioridad, { valor: incidencia.prioridad, tipo: "prioridad" }));

    fila.appendChild(this._celda(incidencia.tecnicoAsignado || "-"));
    fila.appendChild(this._celda(Formatter.fechaLegible(incidencia.fechaCreacion)));
    fila.appendChild(this._celdaAcciones(incidencia));

    return fila;
  }

  _celda(texto) {
    const celda = document.createElement("td");
    celda.textContent = texto;
    return celda;
  }

  _celdaAcciones(incidencia) {
    const celda = document.createElement("td");
    celda.className = "tabla-incidencias-acciones";

    if (typeof this.props.onSeleccionar === "function") {
      const botonVer = document.createElement("button");
      botonVer.type = "button";
      botonVer.className = "boton boton-fantasma boton-sm";
      botonVer.textContent = "Ver detalle";
      this._escuchar(botonVer, "click", () => this.props.onSeleccionar(incidencia));
      celda.appendChild(botonVer);
    }

    if (
      typeof this.props.onCalificar === "function" &&
      incidencia.estado === "RESUELTO" &&
      !incidencia.calificada
    ) {
      const botonCalificar = document.createElement("button");
      botonCalificar.type = "button";
      botonCalificar.className = "boton boton-secundario boton-sm";
      botonCalificar.textContent = "Calificar";
      this._escuchar(botonCalificar, "click", () => this.props.onCalificar(incidencia));
      celda.appendChild(botonCalificar);
    }

    if (typeof this.props.onAtender === "function" && incidencia.estado === "RECIBIDO") {
      const botonAtender = document.createElement("button");
      botonAtender.type = "button";
      botonAtender.className = "boton boton-primario boton-sm";
      botonAtender.textContent = "Atender";
      this._escuchar(botonAtender, "click", () => this.props.onAtender(incidencia));
      celda.appendChild(botonAtender);
    }

    const siguienteEstado = ESTADOS_SIGUIENTES[incidencia.estado];
    if (typeof this.props.onCambiarEstado === "function" && siguienteEstado) {
      const botonCambiar = document.createElement("button");
      botonCambiar.type = "button";
      botonCambiar.className = "boton boton-secundario boton-sm";
      botonCambiar.textContent = `Marcar ${ETIQUETAS_ESTADO[siguienteEstado]}`;
      this._escuchar(botonCambiar, "click", () => this.props.onCambiarEstado(incidencia, siguienteEstado));
      celda.appendChild(botonCambiar);
    }

    return celda;
  }
}
