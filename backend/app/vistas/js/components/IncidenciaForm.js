import { IncidenciaDTO } from "../models/IncidenciaDTO.js";
import { ApiException } from "../utils/ApiException.js";
import { Validators } from "../utils/Validators.js";
import { ComponentBase } from "./ComponentBase.js";
import { Toast } from "./Toast.js";

const TIPOS_REQUERIMIENTO = [
  { valor: "FALLA_TECNICA", texto: "Falla tecnica" },
  { valor: "APERTURA_ANTICIPADA", texto: "Apertura anticipada de laboratorio" },
];

export class IncidenciaForm extends ComponentBase {
  // props: { laboratorioService, equipoService, incidenciaService, evidenciaService, modal, alRegistrar? }
  render() {
    this.contenedor.innerHTML = "";
    this.contenedor.className = "formulario-incidencia";
    this._catalogo = [];

    const formulario = document.createElement("form");
    formulario.className = "formulario-grid";

    const campoDescripcion = this._campoTextarea("Descripcion del problema");
    formulario.appendChild(campoDescripcion.grupo);
    this._campoDescripcion = campoDescripcion.input;

    const campoCategoria = this._campoSelect("Tipo de falla", []);
    formulario.appendChild(campoCategoria.grupo);
    this._selectCategoria = campoCategoria.input;
    this._escuchar(this._selectCategoria, "change", () => this._cargarSubcategorias());

    const campoSubcategoria = this._campoSelect("Falla especifica", []);
    formulario.appendChild(campoSubcategoria.grupo);
    this._selectSubcategoria = campoSubcategoria.input;

    const campoLaboratorio = this._campoSelect("Laboratorio", []);
    formulario.appendChild(campoLaboratorio.grupo);
    this._selectLaboratorio = campoLaboratorio.input;
    this._escuchar(this._selectLaboratorio, "change", () => this._cargarEquipos());

    const campoEquipo = this._campoSelect("Equipo (opcional)", []);
    formulario.appendChild(campoEquipo.grupo);
    this._selectEquipo = campoEquipo.input;

    const campoTipoRequerimiento = this._campoSelect("Tipo de requerimiento", TIPOS_REQUERIMIENTO);
    formulario.appendChild(campoTipoRequerimiento.grupo);
    this._selectTipoRequerimiento = campoTipoRequerimiento.input;

    const campoFecha = this._campoInput("Fecha y hora de inicio de clase", "datetime-local");
    campoFecha.grupo.classList.add("oculto");
    formulario.appendChild(campoFecha.grupo);
    this._grupoFecha = campoFecha.grupo;
    this._campoFecha = campoFecha.input;
    this._escuchar(this._selectTipoRequerimiento, "change", () => {
      const esApertura = this._selectTipoRequerimiento.value === "APERTURA_ANTICIPADA";
      this._grupoFecha.classList.toggle("oculto", !esApertura);
      if (esApertura) {
        this._campoFecha.min = new Date(Date.now() + 60000).toISOString().slice(0, 16);
      }
    });

    const campoArchivo = this._campoInput("Evidencia fotografica (opcional)", "file");
    campoArchivo.input.accept = "image/*";
    campoArchivo.grupo.className = "campo-formulario campo-formulario-ancho";
    formulario.appendChild(campoArchivo.grupo);
    this._campoArchivo = campoArchivo.input;

    const botonEnviar = document.createElement("button");
    botonEnviar.type = "submit";
    botonEnviar.className = "boton boton-primario campo-formulario-ancho";
    botonEnviar.textContent = "Registrar incidencia";
    formulario.appendChild(botonEnviar);

    this.contenedor.appendChild(formulario);
    this._escuchar(formulario, "submit", (evento) => {
      evento.preventDefault();
      this._enviar();
    });

    this._cargarCatalogo();
    this._cargarLaboratorios();
  }

  _campoTextarea(etiquetaTexto) {
    const grupo = document.createElement("div");
    grupo.className = "campo-formulario campo-formulario-ancho";
    const etiqueta = document.createElement("label");
    etiqueta.textContent = etiquetaTexto;
    grupo.appendChild(etiqueta);
    const input = document.createElement("textarea");
    input.required = true;
    input.placeholder = "Ej: El proyector del Lab 1 no enciende";
    grupo.appendChild(input);
    return { grupo, input };
  }

  _campoSelect(etiquetaTexto, opciones) {
    const grupo = document.createElement("div");
    grupo.className = "campo-formulario";
    const etiqueta = document.createElement("label");
    etiqueta.textContent = etiquetaTexto;
    grupo.appendChild(etiqueta);
    const input = document.createElement("select");
    for (const opcion of opciones) {
      const elementoOpcion = document.createElement("option");
      elementoOpcion.value = opcion.valor;
      elementoOpcion.textContent = opcion.texto;
      input.appendChild(elementoOpcion);
    }
    grupo.appendChild(input);
    return { grupo, input };
  }

  _campoInput(etiquetaTexto, tipo) {
    const grupo = document.createElement("div");
    grupo.className = "campo-formulario";
    const etiqueta = document.createElement("label");
    etiqueta.textContent = etiquetaTexto;
    grupo.appendChild(etiqueta);
    const input = document.createElement("input");
    input.type = tipo;
    grupo.appendChild(input);
    return { grupo, input };
  }

  async _cargarCatalogo() {
    try {
      const catalogo = await this.props.incidenciaService.obtenerCatalogo();
      this._catalogo = catalogo.map((entrada) => ({
        categoria: entrada.categoria,
        etiqueta: entrada.etiqueta,
        subcategorias: entrada.subcategorias.map((sub) => ({ nombre: sub.nombre, tipoFalla: sub.tipo_falla })),
      }));
      this._selectCategoria.innerHTML = "";
      for (const entrada of this._catalogo) {
        const opcion = document.createElement("option");
        opcion.value = entrada.categoria;
        opcion.textContent = entrada.etiqueta;
        this._selectCategoria.appendChild(opcion);
      }
      this._cargarSubcategorias();
    } catch {
      // si falla el catalogo el formulario sigue usable con las demas secciones
    }
  }

  _cargarSubcategorias(subcategoriaPreferida = null) {
    const entrada = this._catalogo.find((item) => item.categoria === this._selectCategoria.value);
    this._selectSubcategoria.innerHTML = "";
    for (const sub of entrada?.subcategorias || []) {
      const opcion = document.createElement("option");
      opcion.value = sub.nombre;
      opcion.textContent = sub.nombre;
      opcion.dataset.tipoFalla = sub.tipoFalla;
      this._selectSubcategoria.appendChild(opcion);
    }
    if (subcategoriaPreferida) {
      this._selectSubcategoria.value = subcategoriaPreferida;
    }
  }

  async _cargarLaboratorios() {
    const laboratorios = await this.props.laboratorioService.listar();
    this._laboratorios = laboratorios.filter((laboratorio) => laboratorio.estadoOperativo !== false);
    this._selectLaboratorio.innerHTML = "";
    for (const laboratorio of this._laboratorios) {
      const opcion = document.createElement("option");
      opcion.value = laboratorio.idLaboratorio;
      opcion.textContent = laboratorio.nombre;
      this._selectLaboratorio.appendChild(opcion);
    }
    await this._cargarEquipos();
  }

  async _cargarEquipos() {
    const idLaboratorio = Number(this._selectLaboratorio.value);
    this._selectEquipo.innerHTML = '<option value="">Sin equipo especifico</option>';
    if (!idLaboratorio) {
      return;
    }
    const equipos = await this.props.equipoService.listarPorLaboratorio(idLaboratorio);
    for (const equipo of equipos) {
      const opcion = document.createElement("option");
      opcion.value = equipo.idEquipo;
      opcion.textContent = `${equipo.codigoPatrimonial} - ${equipo.tipoEquipo}`;
      this._selectEquipo.appendChild(opcion);
    }
  }

  /** Llamado por el ChatbotWidget cuando el docente confirma crear un ticket con los datos sugeridos. */
  aplicarSugerencia(sugerencia) {
    this._campoDescripcion.value = sugerencia.descripcion || "";
    if (sugerencia.idLaboratorio) {
      this._selectLaboratorio.value = String(sugerencia.idLaboratorio);
      this._cargarEquipos();
    }
    if (sugerencia.categoria) {
      this._selectCategoria.value = sugerencia.categoria;
      const entrada = this._catalogo.find((item) => item.categoria === sugerencia.categoria);
      const coincidencia = entrada?.subcategorias.find((sub) => sub.tipoFalla === sugerencia.tipoFalla);
      this._cargarSubcategorias(coincidencia?.nombre || null);
    }
    Toast.info("Se aplicaron los datos sugeridos por el asistente. Revisalos y confirma el registro.");
    this.contenedor.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  _tipoFallaSeleccionado() {
    const opcion = this._selectSubcategoria.selectedOptions[0];
    return opcion?.dataset.tipoFalla || null;
  }

  async _enviar() {
    try {
      const tipoRequerimiento = this._selectTipoRequerimiento.value;
      const fechaHoraApertura =
        tipoRequerimiento === "APERTURA_ANTICIPADA" && this._campoFecha.value
          ? new Date(this._campoFecha.value).toISOString()
          : null;
      const tipoFalla = this._tipoFallaSeleccionado();
      if (!tipoFalla) {
        Toast.error("Selecciona el tipo de falla y la falla especifica");
        return;
      }

      const datos = new IncidenciaDTO(
        this._campoDescripcion.value,
        tipoFalla,
        Number(this._selectLaboratorio.value),
        this._selectEquipo.value ? Number(this._selectEquipo.value) : null,
        tipoRequerimiento,
        fechaHoraApertura,
        this._selectSubcategoria.value || null,
      );

      const incidenciaRegistrada = await this.props.incidenciaService.registrar(datos);

      const archivo = this._campoArchivo.files[0];
      if (archivo && this.props.evidenciaService) {
        await this.props.evidenciaService.subir(incidenciaRegistrada.idIncidencia, archivo);
      }

      this._mostrarConfirmacion(incidenciaRegistrada.codigoTicket);
      this._campoDescripcion.value = "";
      this._campoArchivo.value = "";

      if (typeof this.props.alRegistrar === "function") {
        this.props.alRegistrar(incidenciaRegistrada);
      }
    } catch (error) {
      const mensaje = error instanceof ApiException ? error.message : "No se pudo registrar la incidencia";
      Toast.error(mensaje);
    }
  }

  _mostrarConfirmacion(codigoTicket) {
    const modal = this.props.modal;
    if (!modal) {
      Toast.exito(`Incidencia ${codigoTicket} registrada`);
      return;
    }
    modal.abrir(`
      <h3>Incidencia registrada</h3>
      <p class="modal-mensaje">Tu codigo de seguimiento es <strong>${codigoTicket}</strong>. Podras ver su avance en tu historial.</p>
      <div class="modal-acciones">
        <button type="button" class="boton boton-primario" data-accion="cerrar">Entendido</button>
      </div>
    `);
    modal.contenedor
      .querySelector('[data-accion="cerrar"]')
      ?.addEventListener("click", () => modal.cerrar(), { once: true });
  }
}
