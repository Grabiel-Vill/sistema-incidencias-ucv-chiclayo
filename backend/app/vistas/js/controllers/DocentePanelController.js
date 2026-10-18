import { ChatbotWidget } from "../components/ChatbotWidget.js";
import { IncidenciaForm } from "../components/IncidenciaForm.js";
import { IncidenciaTable } from "../components/IncidenciaTable.js";
import { Loader } from "../components/Loader.js";
import { Modal } from "../components/Modal.js";
import { Toast } from "../components/Toast.js";
import { IncidenciaDTO } from "../models/IncidenciaDTO.js";
import { ChatbotService } from "../services/ChatbotService.js";
import { EquipoService } from "../services/EquipoService.js";
import { EvidenciaService } from "../services/EvidenciaService.js";
import { IncidenciaService } from "../services/IncidenciaService.js";
import { LaboratorioService } from "../services/LaboratorioService.js";
import { ApiException } from "../utils/ApiException.js";
import { Formatter } from "../utils/Formatter.js";
import { Icons } from "../utils/Icons.js";
import { Validators } from "../utils/Validators.js";
import { PageControllerBase } from "./PageControllerBase.js";

const ETIQUETAS_ESTADO_DOCENTE = { PROGRAMADO: "Tecnico asignado" };

const FILTROS_ESTADO = [
  { valor: "TODOS", texto: "Todos" },
  { valor: "PENDIENTE", texto: "Pendiente" },
  { valor: "EN_PROCESO", texto: "En proceso" },
  { valor: "RESUELTO", texto: "Resuelto" },
];

export class DocentePanelController extends PageControllerBase {
  constructor(contenedor) {
    super(contenedor, ["DOCENTE"], "Mi panel");
  }

  inicializar() {
    this.laboratorioService = new LaboratorioService(this.http);
    this.equipoService = new EquipoService(this.http);
    this.incidenciaService = new IncidenciaService(this.http);
    this.evidenciaService = new EvidenciaService(this.http);
    this.chatbotService = new ChatbotService(this.http);

    this.modal = new Modal(document.getElementById("contenedor-modal"));
    this._incidencias = [];
    this._filtroTexto = "";
    this._filtroEstado = "TODOS";

    this._montarAtajoApertura();
    this._montarFormulario();
    this._montarChatbot();
    this._montarFiltros();
    this._contenedorTabla = document.getElementById("contenedor-tabla-incidencias");
    this._cargarIncidencias();
  }

  _montarFormulario() {
    const contenedorFormulario = document.getElementById("contenedor-formulario-incidencia");
    this.formulario = new IncidenciaForm(contenedorFormulario, {
      laboratorioService: this.laboratorioService,
      equipoService: this.equipoService,
      incidenciaService: this.incidenciaService,
      evidenciaService: this.evidenciaService,
      modal: this.modal,
      alRegistrar: () => this._cargarIncidencias(),
    });
  }

  _montarAtajoApertura() {
    const contenedor = document.getElementById("contenedor-atajo-apertura");
    if (!contenedor) {
      return;
    }
    contenedor.className = "atajo-apertura";
    contenedor.innerHTML = "";

    const icono = document.createElement("span");
    icono.className = "atajo-apertura-icono";
    icono.innerHTML = Icons.svg("laboratorio", { tamano: 22, color: "var(--color-acento)" });
    contenedor.appendChild(icono);

    const texto = document.createElement("div");
    texto.className = "atajo-apertura-texto";
    texto.innerHTML =
      "<strong>¿Necesitas el laboratorio abierto antes de tu clase?</strong>" +
      "<p>Pide la apertura anticipada desde aquí, sin tener que ir a buscar a nadie.</p>";
    contenedor.appendChild(texto);

    const boton = document.createElement("button");
    boton.type = "button";
    boton.className = "boton boton-secundario";
    boton.textContent = "Solicitar apertura de laboratorio";
    boton.addEventListener("click", () => this._abrirSolicitudApertura());
    contenedor.appendChild(boton);
  }

  async _abrirSolicitudApertura() {
    this.modal.abrir('<p class="modal-mensaje">Cargando laboratorios...</p>');

    let laboratorios = [];
    try {
      laboratorios = (await this.laboratorioService.listar()).filter((lab) => lab.estadoOperativo !== false);
    } catch (error) {
      const mensaje = error instanceof ApiException ? error.message : "No se pudieron cargar los laboratorios";
      Toast.error(mensaje);
      this.modal.cerrar();
      return;
    }

    if (laboratorios.length === 0) {
      this.modal.abrir(`
        <h3>Solicitar apertura de laboratorio</h3>
        <p class="modal-mensaje">No hay laboratorios operativos disponibles en este momento.</p>
        <div class="modal-acciones">
          <button type="button" class="boton boton-secundario" data-accion="cerrar">Cerrar</button>
        </div>
      `);
      this.modal.contenedor
        .querySelector('[data-accion="cerrar"]')
        ?.addEventListener("click", () => this.modal.cerrar(), { once: true });
      return;
    }

    const opcionesLaboratorio = laboratorios
      .map((lab) => `<option value="${lab.idLaboratorio}">${lab.nombre}</option>`)
      .join("");
    const minimoFecha = new Date(Date.now() + 60000).toISOString().slice(0, 16);

    this.modal.abrir(`
      <h3>Solicitar apertura de laboratorio</h3>
      <p class="texto-tenue">Esto crea un ticket de apertura anticipada; un administrador asignará a alguien para que te lo abra.</p>
      <form class="formulario-atencion">
        <div class="campo-formulario">
          <label>Laboratorio</label>
          <select class="campo-apertura-laboratorio">${opcionesLaboratorio}</select>
        </div>
        <div class="campo-formulario">
          <label>Fecha y hora en que necesitas el laboratorio abierto</label>
          <input type="datetime-local" class="campo-apertura-fecha" min="${minimoFecha}" required />
        </div>
        <div class="campo-formulario">
          <label>Motivo</label>
          <textarea class="campo-apertura-motivo" placeholder="Ej: Clase de laboratorio a las 8am, necesito que esté abierto 10 minutos antes"></textarea>
        </div>
        <div class="modal-acciones">
          <button type="button" class="boton boton-secundario" data-accion="cancelar">Cancelar</button>
          <button type="submit" class="boton boton-primario">Enviar solicitud</button>
        </div>
      </form>
    `);

    const caja = this.modal.contenedor;
    caja.querySelector('[data-accion="cancelar"]')?.addEventListener("click", () => this.modal.cerrar(), {
      once: true,
    });
    caja.querySelector(".formulario-atencion").addEventListener("submit", (evento) => {
      evento.preventDefault();
      this._enviarSolicitudApertura(caja);
    });
  }

  async _enviarSolicitudApertura(caja) {
    const idLaboratorio = Number(caja.querySelector(".campo-apertura-laboratorio").value);
    const fechaLocal = caja.querySelector(".campo-apertura-fecha").value;
    const motivo = caja.querySelector(".campo-apertura-motivo").value.trim();
    const fechaIso = fechaLocal ? new Date(fechaLocal).toISOString() : null;

    if (!motivo) {
      Toast.error("Cuéntanos brevemente el motivo de la apertura");
      return;
    }
    if (!Validators.esFechaFutura(fechaIso)) {
      Toast.error("Elige una fecha y hora futura para la apertura");
      return;
    }

    try {
      const datos = new IncidenciaDTO(motivo, null, idLaboratorio, null, "APERTURA_ANTICIPADA", fechaIso, null);
      const incidenciaRegistrada = await this.incidenciaService.registrar(datos);
      this.modal.abrir(`
        <h3>Solicitud enviada</h3>
        <p class="modal-mensaje">Tu código de seguimiento es <strong>${incidenciaRegistrada.codigoTicket}</strong>. Un administrador la asignará para que te abran el laboratorio a tiempo.</p>
        <div class="modal-acciones">
          <button type="button" class="boton boton-primario" data-accion="cerrar">Entendido</button>
        </div>
      `);
      this.modal.contenedor
        .querySelector('[data-accion="cerrar"]')
        ?.addEventListener("click", () => this.modal.cerrar(), { once: true });
      this._cargarIncidencias();
    } catch (error) {
      const mensaje = error instanceof ApiException ? error.message : "No se pudo registrar la solicitud";
      Toast.error(mensaje);
    }
  }

  _montarChatbot() {
    const contenedorChatbot = document.getElementById("contenedor-chatbot");
    this.chatbot = new ChatbotWidget(contenedorChatbot, {
      chatbotService: this.chatbotService,
      laboratorioService: this.laboratorioService,
      onCrearTicketSugerido: (sugerencia) => this.formulario.aplicarSugerencia(sugerencia),
    });
  }

  _montarFiltros() {
    const contenedor = document.getElementById("contenedor-filtros-historial");
    if (!contenedor) {
      return;
    }
    contenedor.className = "barra-filtros";
    contenedor.innerHTML = "";

    const campoBusqueda = document.createElement("input");
    campoBusqueda.type = "search";
    campoBusqueda.placeholder = "Buscar por codigo o descripcion...";
    campoBusqueda.className = "barra-filtros-busqueda";
    campoBusqueda.addEventListener("input", () => {
      this._filtroTexto = campoBusqueda.value.trim().toLowerCase();
      this._renderizarTabla();
    });
    contenedor.appendChild(campoBusqueda);

    const grupoBotones = document.createElement("div");
    grupoBotones.className = "barra-filtros-botones";
    this._botonesFiltro = [];
    for (const filtro of FILTROS_ESTADO) {
      const boton = document.createElement("button");
      boton.type = "button";
      boton.className = "boton boton-fantasma boton-sm filtro-estado";
      boton.textContent = filtro.texto;
      boton.dataset.valor = filtro.valor;
      boton.classList.toggle("filtro-estado-activo", filtro.valor === this._filtroEstado);
      boton.addEventListener("click", () => {
        this._filtroEstado = filtro.valor;
        for (const otroBoton of this._botonesFiltro) {
          otroBoton.classList.toggle("filtro-estado-activo", otroBoton.dataset.valor === filtro.valor);
        }
        this._renderizarTabla();
      });
      this._botonesFiltro.push(boton);
      grupoBotones.appendChild(boton);
    }
    contenedor.appendChild(grupoBotones);
  }

  async _cargarIncidencias() {
    this.tabla?.destruir();
    new Loader(this._contenedorTabla, { texto: "Cargando tus incidencias..." });
    try {
      this._incidencias = await this.incidenciaService.listarMias();
      this._renderizarTabla();
    } catch (error) {
      const mensaje = error instanceof ApiException ? error.message : "No se pudieron cargar las incidencias";
      Toast.error(mensaje);
    }
  }

  _renderizarTabla() {
    this.tabla?.destruir();
    const incidencias = this._incidencias.filter((incidencia) => this._cumpleFiltro(incidencia));
    this.tabla = new IncidenciaTable(this._contenedorTabla, {
      incidencias,
      etiquetasEstado: ETIQUETAS_ESTADO_DOCENTE,
      onSeleccionar: (incidencia) => this._verDetalle(incidencia),
      onCalificar: (incidencia) => this._calificar(incidencia),
    });
  }

  _cumpleFiltro(incidencia) {
    if (this._filtroEstado === "PENDIENTE" && !["RECIBIDO", "PROGRAMADO"].includes(incidencia.estado)) {
      return false;
    }
    if (this._filtroEstado === "EN_PROCESO" && incidencia.estado !== "EN_PROCESO") {
      return false;
    }
    if (this._filtroEstado === "RESUELTO" && incidencia.estado !== "RESUELTO") {
      return false;
    }
    if (!this._filtroTexto) {
      return true;
    }
    return (
      incidencia.codigoTicket.toLowerCase().includes(this._filtroTexto) ||
      incidencia.descripcion.toLowerCase().includes(this._filtroTexto)
    );
  }

  _verDetalle(incidencia) {
    const pasos = [
      { etiqueta: "Recibido", hecho: true, fecha: incidencia.fechaCreacion },
      {
        etiqueta: "Tecnico asignado",
        hecho: Boolean(incidencia.tecnicoAsignado),
        detalle: incidencia.tecnicoAsignado,
      },
      { etiqueta: "En proceso", hecho: Boolean(incidencia.fechaAtencion), fecha: incidencia.fechaAtencion },
      { etiqueta: "Resuelto", hecho: Boolean(incidencia.fechaResolucion), fecha: incidencia.fechaResolucion },
    ];

    const pasosHtml = pasos
      .map(
        (paso) => `
      <li class="timeline-paso ${paso.hecho ? "timeline-paso-hecho" : ""}">
        <span class="timeline-punto"></span>
        <div>
          <strong>${paso.etiqueta}</strong>
          ${paso.detalle ? `<span class="timeline-detalle">${paso.detalle}</span>` : ""}
          ${paso.fecha ? `<span class="timeline-fecha">${Formatter.fechaLegible(paso.fecha)}</span>` : ""}
        </div>
      </li>`,
      )
      .join("");

    const notasHtml = incidencia.notasPublicas.length
      ? `<ul class="timeline-notas">${incidencia.notasPublicas.map((nota) => `<li>${nota}</li>`).join("")}</ul>`
      : `<p class="modal-mensaje">Aun no hay notas publicas del tecnico.</p>`;

    this.modal.abrir(`
      <h3>${incidencia.codigoTicket}</h3>
      <p class="modal-mensaje">${incidencia.descripcion}</p>
      <ol class="timeline-incidencia">${pasosHtml}</ol>
      <h4>Notas del tecnico</h4>
      ${notasHtml}
      <div class="modal-acciones">
        <button type="button" class="boton boton-secundario" data-accion="cerrar">Cerrar</button>
      </div>
    `);
    this.modal.contenedor
      .querySelector('[data-accion="cerrar"]')
      ?.addEventListener("click", () => this.modal.cerrar(), { once: true });
  }

  _calificar(incidencia) {
    this.modal.abrir(`
      <h3>Calificar atencion</h3>
      <p class="modal-mensaje">Ticket ${incidencia.codigoTicket}</p>
      <div class="calificacion-estrellas">
        ${[1, 2, 3, 4, 5]
          .map(
            (n) =>
              `<button type="button" class="calificacion-estrella" data-valor="${n}" aria-label="${n} estrellas">${Icons.svg(
                "estrella",
                { tamano: 28 },
              )}</button>`,
          )
          .join("")}
      </div>
      <textarea class="calificacion-comentario" placeholder="Comentario (opcional)"></textarea>
      <div class="modal-acciones">
        <button type="button" class="boton boton-secundario" data-accion="cancelar">Cancelar</button>
        <button type="button" class="boton boton-primario" data-accion="enviar" disabled>Enviar calificacion</button>
      </div>
    `);

    const caja = this.modal.contenedor;
    const botonesEstrella = [...caja.querySelectorAll(".calificacion-estrella")];
    const botonEnviar = caja.querySelector('[data-accion="enviar"]');
    const campoComentario = caja.querySelector(".calificacion-comentario");
    let estrellasSeleccionadas = 0;

    for (const [indice, boton] of botonesEstrella.entries()) {
      boton.addEventListener("click", () => {
        estrellasSeleccionadas = indice + 1;
        for (const [i, b] of botonesEstrella.entries()) {
          b.classList.toggle("calificacion-estrella-activa", i < estrellasSeleccionadas);
        }
        botonEnviar.disabled = false;
      });
    }

    caja.querySelector('[data-accion="cancelar"]')?.addEventListener("click", () => this.modal.cerrar(), {
      once: true,
    });
    botonEnviar.addEventListener(
      "click",
      async () => {
        try {
          await this.incidenciaService.calificar(
            incidencia.idIncidencia,
            estrellasSeleccionadas,
            campoComentario.value.trim() || null,
          );
          Toast.exito("Gracias por tu calificacion");
          this.modal.cerrar();
          this._cargarIncidencias();
        } catch (error) {
          const mensaje = error instanceof ApiException ? error.message : "No se pudo registrar la calificacion";
          Toast.error(mensaje);
        }
      },
      { once: true },
    );
  }
}
