import { IncidenciaTable } from "../components/IncidenciaTable.js";
import { Loader } from "../components/Loader.js";
import { Modal } from "../components/Modal.js";
import { StatCard } from "../components/StatCard.js";
import { Toast } from "../components/Toast.js";
import { API_BASE_URL } from "../config.js";
import { NotaTecnicaDTO } from "../models/NotaTecnicaDTO.js";
import { EvidenciaService } from "../services/EvidenciaService.js";
import { IncidenciaService } from "../services/IncidenciaService.js";
import { NotaTecnicaService } from "../services/NotaTecnicaService.js";
import { ApiException } from "../utils/ApiException.js";
import { Formatter } from "../utils/Formatter.js";

import { PageControllerBase } from "./PageControllerBase.js";

const ETIQUETAS_ESTADO_TECNICO = { PROGRAMADO: "Pendiente" };
const ESTADOS_TEXTO = { RECIBIDO: "Recibido", PROGRAMADO: "Pendiente", EN_PROCESO: "En proceso", RESUELTO: "Resuelto" };

// Espejo de app/models/incidencia.py::_TRANSICIONES_VALIDAS (ver docs/ARQUITECTURA.md): el
// backend es quien realmente valida esto, aca solo evitamos ofrecer transiciones invalidas.
const TRANSICIONES_VALIDAS = {
  RECIBIDO: ["PROGRAMADO", "EN_PROCESO"],
  PROGRAMADO: ["EN_PROCESO", "RESUELTO"],
  EN_PROCESO: ["RESUELTO"],
  RESUELTO: [],
};

const FILTROS_ESTADO = [
  { valor: "", texto: "Todos los estados" },
  { valor: "PROGRAMADO", texto: "Pendiente" },
  { valor: "EN_PROCESO", texto: "En proceso" },
  { valor: "RESUELTO", texto: "Resuelto" },
];

const FILTROS_PRIORIDAD = [
  { valor: "", texto: "Todas las prioridades" },
  { valor: "ALTA", texto: "Alta" },
  { valor: "MEDIA", texto: "Media" },
  { valor: "BAJA", texto: "Baja" },
];

export class TecnicoBandejaController extends PageControllerBase {
  constructor(contenedor) {
    super(contenedor, ["TECNICO"], "Bandeja tecnica");
  }

  inicializar() {
    this.incidenciaService = new IncidenciaService(this.http);
    this.notaTecnicaService = new NotaTecnicaService(this.http);
    this.evidenciaService = new EvidenciaService(this.http);
    this.modal = new Modal(document.getElementById("contenedor-modal"));

    this._incidencias = [];
    this._filtroEstado = "";
    this._filtroPrioridad = "";
    this._filtroTexto = "";

    this._montarFiltros();
    this._contenedorTabla = document.getElementById("contenedor-tabla-incidencias");
    this._cargarMetricas();
    this._cargarIncidencias();
  }

  async _cargarMetricas() {
    const contenedor = document.getElementById("contenedor-stats");
    if (!contenedor) {
      return;
    }
    try {
      const metricas = await this.incidenciaService.obtenerMisMetricas();
      for (const card of this.statCards || []) {
        card.destruir();
      }
      contenedor.innerHTML = "";
      contenedor.className = "contenedor-stats";
      const datos = [
        { titulo: "Pendientes", valor: String(metricas.pendientes), icono: "reloj" },
        { titulo: "En proceso", valor: String(metricas.en_proceso), icono: "bandeja" },
        { titulo: "Resueltos este mes", valor: String(metricas.resueltos_mes), icono: "check" },
      ];
      this.statCards = datos.map((dato) => {
        const espacio = document.createElement("div");
        contenedor.appendChild(espacio);
        return new StatCard(espacio, dato);
      });
    } catch (error) {
      this._mostrarError(error, "No se pudieron cargar las metricas");
    }
  }

  _montarFiltros() {
    const contenedor = document.getElementById("contenedor-filtros");
    contenedor.innerHTML = "";
    contenedor.className = "barra-filtros";

    const campoBusqueda = document.createElement("input");
    campoBusqueda.type = "search";
    campoBusqueda.placeholder = "Buscar por codigo...";
    campoBusqueda.className = "barra-filtros-busqueda";
    campoBusqueda.addEventListener("input", () => {
      this._filtroTexto = campoBusqueda.value.trim().toLowerCase();
      this._renderizarTabla();
    });
    contenedor.appendChild(campoBusqueda);

    const grupoSelects = document.createElement("div");
    grupoSelects.className = "barra-filtros-botones";
    grupoSelects.appendChild(
      this._crearSelectFiltro(FILTROS_ESTADO, (valor) => {
        this._filtroEstado = valor;
        this._cargarIncidencias();
      }),
    );
    grupoSelects.appendChild(
      this._crearSelectFiltro(FILTROS_PRIORIDAD, (valor) => {
        this._filtroPrioridad = valor;
        this._renderizarTabla();
      }),
    );
    contenedor.appendChild(grupoSelects);
  }

  _crearSelectFiltro(opciones, alCambiar) {
    const select = document.createElement("select");
    for (const opcion of opciones) {
      const elementoOpcion = document.createElement("option");
      elementoOpcion.value = opcion.valor;
      elementoOpcion.textContent = opcion.texto;
      select.appendChild(elementoOpcion);
    }
    select.addEventListener("change", () => alCambiar(select.value));
    return select;
  }

  async _cargarIncidencias() {
    this.tabla?.destruir();
    new Loader(this._contenedorTabla, { texto: "Cargando incidencias..." });
    try {
      // El backend ya restringe esta lista a los tickets asignados a este tecnico (ver
      // incidencia_controller.listar_incidencias); el filtro de estado si viaja al servidor.
      this._incidencias = await this.incidenciaService.listarConFiltro({
        estado: this._filtroEstado || undefined,
      });
      this._renderizarTabla();
    } catch (error) {
      this._mostrarError(error, "No se pudieron cargar las incidencias");
    }
  }

  _renderizarTabla() {
    this.tabla?.destruir();
    const incidencias = this._incidencias.filter((incidencia) => this._cumpleFiltro(incidencia));
    this.tabla = new IncidenciaTable(this._contenedorTabla, {
      incidencias,
      etiquetasEstado: ETIQUETAS_ESTADO_TECNICO,
      onSeleccionar: (incidencia) => this._abrirDetalle(incidencia),
    });
  }

  _cumpleFiltro(incidencia) {
    if (this._filtroPrioridad && incidencia.prioridad !== this._filtroPrioridad) {
      return false;
    }
    if (!this._filtroTexto) {
      return true;
    }
    return incidencia.codigoTicket.toLowerCase().includes(this._filtroTexto);
  }

  async _abrirDetalle(incidencia) {
    this.modal.abrir('<p class="modal-mensaje">Cargando detalle...</p>');

    let notas = [];
    let evidencias = [];
    try {
      [notas, evidencias] = await Promise.all([
        this.notaTecnicaService.listar(incidencia.idIncidencia),
        this.evidenciaService.listar(incidencia.idIncidencia),
      ]);
    } catch (error) {
      this._mostrarError(error, "No se pudo cargar el detalle del ticket");
    }

    const notasPublicas = notas.filter((nota) => !nota.esPrivado);
    const notasPrivadas = notas.filter((nota) => nota.esPrivado);
    const transicionesDisponibles = TRANSICIONES_VALIDAS[incidencia.estado] || [];

    const evidenciasHtml = evidencias.length
      ? `<div class="detalle-evidencias">${evidencias
          .map(
            (evidencia) =>
              `<img src="${API_BASE_URL}/storage/${evidencia.urlImagen}" alt="Evidencia del docente" class="detalle-evidencia-img" />`,
          )
          .join("")}</div>`
      : `<p class="texto-marcador">El docente no adjunto evidencia.</p>`;

    const listaNotasHtml = (lista, textoVacio) =>
      lista.length
        ? `<ul class="lista-notas">${lista.map((nota) => `<li>${nota.contenido}</li>`).join("")}</ul>`
        : `<p class="texto-marcador">${textoVacio}</p>`;

    const opcionesEstado = [incidencia.estado, ...transicionesDisponibles]
      .map((estado) => `<option value="${estado}">${ESTADOS_TEXTO[estado]}</option>`)
      .join("");

    this.modal.abrir(`
      <h3>${incidencia.codigoTicket}</h3>
      <p class="modal-mensaje">${incidencia.descripcion}</p>
      <dl class="detalle-datos">
        <div><dt>Docente</dt><dd>${incidencia.docente || "-"}</dd></div>
        <div><dt>Laboratorio</dt><dd>${incidencia.laboratorio || "-"}</dd></div>
        <div><dt>Equipo</dt><dd>${incidencia.equipo || "Sin equipo especifico"}</dd></div>
        <div><dt>Falla especifica</dt><dd>${incidencia.subcategoria || "-"}</dd></div>
        ${
          incidencia.fechaHoraApertura
            ? `<div><dt>Apertura solicitada</dt><dd>${Formatter.fechaLegible(incidencia.fechaHoraApertura)}</dd></div>`
            : ""
        }
      </dl>

      <h4>Evidencia del docente</h4>
      ${evidenciasHtml}

      <h4>Notas publicas (visibles para el docente)</h4>
      ${listaNotasHtml(notasPublicas, "Aun no hay notas publicas.")}

      <h4>Notas internas (solo soporte)</h4>
      ${listaNotasHtml(notasPrivadas, "Aun no hay notas internas.")}

      <form class="formulario-atencion">
        <div class="campo-formulario">
          <label>Estado</label>
          <select class="detalle-select-estado" ${transicionesDisponibles.length === 0 ? "disabled" : ""}>
            ${opcionesEstado}
          </select>
        </div>
        <div class="campo-formulario">
          <label>Nota interna (privada, no visible para el docente)</label>
          <textarea class="detalle-nota-privada" placeholder="Diagnostico tecnico, pasos internos..."></textarea>
        </div>
        <div class="campo-formulario">
          <label>Nota publica de diagnostico y solucion (obligatoria para resolver)</label>
          <textarea class="detalle-nota-publica" placeholder="Que se hizo para resolver el problema..."></textarea>
        </div>
        <div class="modal-acciones">
          <button type="button" class="boton boton-secundario" data-accion="cerrar">Cerrar</button>
          <button type="submit" class="boton boton-primario">Guardar cambios y notificar</button>
        </div>
      </form>
    `);

    const caja = this.modal.contenedor;
    caja.querySelector('[data-accion="cerrar"]')?.addEventListener("click", () => this.modal.cerrar(), {
      once: true,
    });
    caja.querySelector(".formulario-atencion").addEventListener("submit", (evento) => {
      evento.preventDefault();
      this._guardarCambios(incidencia, caja);
    });
  }

  async _guardarCambios(incidencia, caja) {
    const nuevoEstado = caja.querySelector(".detalle-select-estado").value;
    const notaPrivada = caja.querySelector(".detalle-nota-privada").value.trim();
    const notaPublica = caja.querySelector(".detalle-nota-publica").value.trim();
    const cambiaEstado = nuevoEstado !== incidencia.estado;

    if (cambiaEstado && nuevoEstado === "RESUELTO" && !notaPublica) {
      Toast.error("Registra una nota publica de diagnostico y solucion antes de resolver el ticket");
      return;
    }

    try {
      if (notaPrivada) {
        await this.notaTecnicaService.agregar(incidencia.idIncidencia, new NotaTecnicaDTO(notaPrivada, true));
      }
      if (notaPublica) {
        await this.notaTecnicaService.agregar(incidencia.idIncidencia, new NotaTecnicaDTO(notaPublica, false));
      }
      if (cambiaEstado) {
        await this.incidenciaService.cambiarEstado(incidencia.idIncidencia, nuevoEstado);
        Toast.exito("Cambios guardados y se notifico al docente");
      } else if (notaPrivada || notaPublica) {
        Toast.exito("Nota guardada");
      }
      this.modal.cerrar();
      this._cargarMetricas();
      this._cargarIncidencias();
    } catch (error) {
      this._mostrarError(error, "No se pudieron guardar los cambios");
    }
  }

  _mostrarError(error, mensajePorDefecto) {
    const mensaje = error instanceof ApiException ? error.message : mensajePorDefecto;
    Toast.error(mensaje);
  }
}
