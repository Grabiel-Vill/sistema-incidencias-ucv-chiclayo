import { Loader } from "../components/Loader.js";
import { Modal } from "../components/Modal.js";
import { StatusBadge } from "../components/StatusBadge.js";
import { Toast } from "../components/Toast.js";
import { IncidenciaService } from "../services/IncidenciaService.js";
import { UsuarioService } from "../services/UsuarioService.js";
import { ApiException } from "../utils/ApiException.js";
import { Formatter } from "../utils/Formatter.js";
import { PageControllerBase } from "./PageControllerBase.js";

const PRIORIDADES = [
  { valor: "ALTA", texto: "Alta" },
  { valor: "MEDIA", texto: "Media" },
  { valor: "BAJA", texto: "Baja" },
];

export class AdminIncidenciasController extends PageControllerBase {
  constructor(contenedor) {
    super(contenedor, ["ADMINISTRADOR"], "Gestion de incidencias");
  }

  inicializar() {
    this.incidenciaService = new IncidenciaService(this.http);
    this.usuarioService = new UsuarioService(this.http);
    this.modal = new Modal(document.getElementById("contenedor-modal"));
    this._contenedorTabla = document.getElementById("contenedor-tabla-incidencias");
    this._badges = [];
    this._cargarIncidencias();
  }

  async _cargarIncidencias() {
    for (const badge of this._badges) {
      badge.destruir();
    }
    this._badges = [];
    new Loader(this._contenedorTabla, { texto: "Cargando incidencias recibidas..." });
    try {
      const incidencias = await this.incidenciaService.listarConFiltro({ estado: "RECIBIDO" });
      this._pintarTabla(incidencias);
    } catch (error) {
      this._mostrarError(error, "No se pudieron cargar las incidencias");
    }
  }

  _pintarTabla(incidencias) {
    this._contenedorTabla.innerHTML = "";

    if (incidencias.length === 0) {
      const vacio = document.createElement("p");
      vacio.className = "texto-marcador";
      vacio.textContent = "No hay incidencias recibidas pendientes de asignar.";
      this._contenedorTabla.appendChild(vacio);
      return;
    }

    const envoltorio = document.createElement("div");
    envoltorio.className = "tabla-incidencias-envoltorio";
    const tabla = document.createElement("table");
    const encabezado = document.createElement("thead");
    encabezado.innerHTML = `
      <tr>
        <th>Codigo</th>
        <th>Laboratorio</th>
        <th>Falla</th>
        <th>Fecha/hora</th>
        <th>Estado</th>
        <th></th>
      </tr>
    `;
    tabla.appendChild(encabezado);

    const cuerpo = document.createElement("tbody");
    for (const incidencia of incidencias) {
      const fila = document.createElement("tr");
      fila.appendChild(this._celda(incidencia.codigoTicket));
      fila.appendChild(this._celda(incidencia.laboratorio || "-"));
      const textoFalla = incidencia.tipoFalla
        ? `${incidencia.tipoFalla}${incidencia.subcategoria ? " - " + incidencia.subcategoria : ""}`
        : "Apertura de laboratorio";
      fila.appendChild(this._celda(textoFalla));
      fila.appendChild(this._celda(Formatter.fechaLegible(incidencia.fechaCreacion)));

      const celdaEstado = document.createElement("td");
      const espacioEstado = document.createElement("span");
      celdaEstado.appendChild(espacioEstado);
      this._badges.push(new StatusBadge(espacioEstado, { valor: incidencia.estado, tipo: "estado" }));
      fila.appendChild(celdaEstado);

      const celdaAccion = document.createElement("td");
      const boton = document.createElement("button");
      boton.type = "button";
      boton.className = "boton boton-primario boton-sm";
      boton.textContent = "Asignar tecnico";
      boton.addEventListener("click", () => this._abrirAsignacion(incidencia));
      celdaAccion.appendChild(boton);
      fila.appendChild(celdaAccion);

      cuerpo.appendChild(fila);
    }
    tabla.appendChild(cuerpo);
    envoltorio.appendChild(tabla);
    this._contenedorTabla.appendChild(envoltorio);
  }

  _celda(texto) {
    const celda = document.createElement("td");
    celda.textContent = texto;
    return celda;
  }

  async _abrirAsignacion(incidencia) {
    this.modal.abrir('<p class="modal-mensaje">Cargando tecnicos...</p>');

    let tecnicosConCarga = [];
    try {
      const [usuarios, carga] = await Promise.all([
        this.usuarioService.listar(),
        this.incidenciaService.obtenerCargaTecnicos(),
      ]);
      tecnicosConCarga = usuarios
        .filter((usuario) => usuario.rol === "TECNICO" && usuario.estado)
        .map((tecnico) => {
          tecnico.ticketsAbiertos = carga[tecnico.idUsuario] || 0;
          return tecnico;
        })
        .sort((a, b) => a.ticketsAbiertos - b.ticketsAbiertos);
    } catch (error) {
      this._mostrarError(error, "No se pudieron cargar los tecnicos");
      this.modal.cerrar();
      return;
    }

    if (tecnicosConCarga.length === 0) {
      this.modal.abrir(`
        <h3>Asignar tecnico</h3>
        <p class="modal-mensaje">No hay tecnicos activos disponibles.</p>
        <div class="modal-acciones">
          <button type="button" class="boton boton-secundario" data-accion="cerrar">Cerrar</button>
        </div>
      `);
      this.modal.contenedor
        .querySelector('[data-accion="cerrar"]')
        ?.addEventListener("click", () => this.modal.cerrar(), { once: true });
      return;
    }

    const opcionesTecnico = tecnicosConCarga
      .map((tecnico, indice) => {
        const plural = tecnico.ticketsAbiertos === 1 ? "" : "s";
        return `
        <label class="opcion-tecnico">
          <input type="radio" name="tecnico" value="${tecnico.idUsuario}" ${indice === 0 ? "checked" : ""} />
          <span>${tecnico.nombreCompleto} - ${tecnico.especialidad || "Sin especialidad"}
            <small>(${tecnico.ticketsAbiertos} ticket${plural} abierto${plural})</small>
          </span>
        </label>`;
      })
      .join("");

    this.modal.abrir(`
      <h3>Asignar tecnico</h3>
      <p class="modal-mensaje">${incidencia.codigoTicket}: ${incidencia.descripcion}</p>
      <p class="texto-tenue">Se sugiere al tecnico con menos tickets abiertos (preseleccionado).</p>
      <div class="lista-opciones-tecnico">${opcionesTecnico}</div>
      <div class="campo-formulario">
        <label>Prioridad</label>
        <select class="select-prioridad-asignacion">
          ${PRIORIDADES.map(
            (prioridad) => `<option value="${prioridad.valor}" ${prioridad.valor === "MEDIA" ? "selected" : ""}>${prioridad.texto}</option>`,
          ).join("")}
        </select>
      </div>
      <div class="modal-acciones">
        <button type="button" class="boton boton-secundario" data-accion="cancelar">Cancelar</button>
        <button type="button" class="boton boton-primario" data-accion="confirmar">Asignar</button>
      </div>
    `);

    const caja = this.modal.contenedor;
    caja.querySelector('[data-accion="cancelar"]')?.addEventListener("click", () => this.modal.cerrar(), {
      once: true,
    });
    caja.querySelector('[data-accion="confirmar"]')?.addEventListener(
      "click",
      async () => {
        const idTecnico = Number(caja.querySelector('input[name="tecnico"]:checked')?.value);
        const prioridad = caja.querySelector(".select-prioridad-asignacion").value;
        if (!idTecnico) {
          Toast.error("Selecciona un tecnico");
          return;
        }
        try {
          await this.incidenciaService.asignarTecnico(incidencia.idIncidencia, idTecnico, prioridad);
          Toast.exito(`Ticket ${incidencia.codigoTicket} asignado`);
          this.modal.cerrar();
          this._cargarIncidencias();
        } catch (error) {
          this._mostrarError(error, "No se pudo asignar el tecnico");
        }
      },
      { once: true },
    );
  }

  _mostrarError(error, mensajePorDefecto) {
    const mensaje = error instanceof ApiException ? error.message : mensajePorDefecto;
    Toast.error(mensaje);
  }
}
