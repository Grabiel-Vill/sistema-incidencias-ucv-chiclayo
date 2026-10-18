import { Loader } from "../components/Loader.js";
import { Modal } from "../components/Modal.js";
import { StatusBadge } from "../components/StatusBadge.js";
import { Toast } from "../components/Toast.js";
import { EquipoDTO } from "../models/EquipoDTO.js";
import { LaboratorioDTO } from "../models/LaboratorioDTO.js";
import { EquipoService } from "../services/EquipoService.js";
import { LaboratorioService } from "../services/LaboratorioService.js";
import { ApiException } from "../utils/ApiException.js";
import { PageControllerBase } from "./PageControllerBase.js";

const ESTADOS_EQUIPO = [
  { valor: "OPERATIVO", texto: "Operativo" },
  { valor: "DEFECTUOSO", texto: "Defectuoso" },
  { valor: "EN_MANTENIMIENTO", texto: "En mantenimiento" },
];

export class AdminLaboratoriosController extends PageControllerBase {
  constructor(contenedor) {
    super(contenedor, ["ADMINISTRADOR"], "Laboratorios");
  }

  inicializar() {
    this.laboratorioService = new LaboratorioService(this.http);
    this.equipoService = new EquipoService(this.http);
    this.modal = new Modal(document.getElementById("contenedor-modal"));
    this._badges = [];
    this._idLaboratorioEnEdicion = null;
    this._estadoOperativoEnEdicion = true;

    this._montarFormulario();
    this._contenedorLista = document.getElementById("contenedor-lista-laboratorios");
    this._cargarLaboratorios();
  }

  _campo(etiquetaTexto, elementoInput) {
    const grupo = document.createElement("div");
    grupo.className = "campo-formulario";
    const etiqueta = document.createElement("label");
    etiqueta.textContent = etiquetaTexto;
    grupo.appendChild(etiqueta);
    grupo.appendChild(elementoInput);
    return grupo;
  }

  _montarFormulario() {
    const contenedor = document.getElementById("contenedor-formulario-laboratorio");
    contenedor.innerHTML = "";

    this._formularioLaboratorio = document.createElement("form");
    this._formularioLaboratorio.className = "formulario-grid";

    this._campoNombre = document.createElement("input");
    this._formularioLaboratorio.appendChild(this._campo("Nombre del laboratorio", this._campoNombre));

    this._campoPabellon = document.createElement("input");
    this._formularioLaboratorio.appendChild(this._campo("Pabellon", this._campoPabellon));

    this._campoPiso = document.createElement("input");
    this._campoPiso.type = "number";
    this._formularioLaboratorio.appendChild(this._campo("Piso", this._campoPiso));

    this._botonGuardarLaboratorio = document.createElement("button");
    this._botonGuardarLaboratorio.type = "submit";
    this._botonGuardarLaboratorio.className = "boton boton-primario campo-formulario-ancho";
    this._botonGuardarLaboratorio.textContent = "Registrar laboratorio";
    this._formularioLaboratorio.appendChild(this._botonGuardarLaboratorio);

    contenedor.appendChild(this._formularioLaboratorio);

    this._formularioLaboratorio.addEventListener("submit", async (evento) => {
      evento.preventDefault();
      try {
        const datos = new LaboratorioDTO(
          this._campoNombre.value,
          this._campoPabellon.value,
          Number(this._campoPiso.value),
          this._idLaboratorioEnEdicion ? this._estadoOperativoEnEdicion : true,
        );
        if (this._idLaboratorioEnEdicion) {
          await this.laboratorioService.editar(this._idLaboratorioEnEdicion, datos);
          Toast.exito("Laboratorio actualizado");
        } else {
          await this.laboratorioService.registrar(datos);
          Toast.exito("Laboratorio registrado");
        }
        this._salirModoEdicion();
        this._cargarLaboratorios();
      } catch (error) {
        const mensaje = error instanceof ApiException ? error.message : "No se pudo guardar el laboratorio";
        Toast.error(mensaje);
      }
    });
  }

  _entrarModoEdicion(laboratorio) {
    this._idLaboratorioEnEdicion = laboratorio.idLaboratorio;
    this._estadoOperativoEnEdicion = laboratorio.estadoOperativo;
    this._campoNombre.value = laboratorio.nombre;
    this._campoPabellon.value = laboratorio.pabellon;
    this._campoPiso.value = laboratorio.piso;
    this._botonGuardarLaboratorio.textContent = "Guardar cambios";
    this._formularioLaboratorio.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  _salirModoEdicion() {
    this._idLaboratorioEnEdicion = null;
    this._estadoOperativoEnEdicion = true;
    this._formularioLaboratorio.reset();
    this._botonGuardarLaboratorio.textContent = "Registrar laboratorio";
  }

  async _alternarEstadoOperativo(laboratorio) {
    const pasarAMantenimiento = laboratorio.estadoOperativo;
    const mensaje = pasarAMantenimiento
      ? `Vas a poner "${laboratorio.nombre}" en mantenimiento. No aparecera como opcion para tickets nuevos del docente hasta que lo marques operativo de nuevo. Continuar?`
      : `Vas a marcar "${laboratorio.nombre}" como operativo nuevamente. Continuar?`;
    const confirmado = await this.modal.confirmar(mensaje, {
      tituloConfirmar: pasarAMantenimiento ? "Pasar a mantenimiento" : "Marcar operativo",
      peligroso: pasarAMantenimiento,
    });
    if (!confirmado) {
      return;
    }
    try {
      const datos = new LaboratorioDTO(
        laboratorio.nombre,
        laboratorio.pabellon,
        laboratorio.piso,
        !laboratorio.estadoOperativo,
      );
      await this.laboratorioService.editar(laboratorio.idLaboratorio, datos);
      Toast.exito("Estado del laboratorio actualizado");
      this._cargarLaboratorios();
    } catch (error) {
      const mensajeError = error instanceof ApiException ? error.message : "No se pudo actualizar el laboratorio";
      Toast.error(mensajeError);
    }
  }

  async _cargarLaboratorios() {
    new Loader(this._contenedorLista, { texto: "Cargando laboratorios..." });
    try {
      const laboratorios = await this.laboratorioService.listar();
      await this._pintarLista(laboratorios);
    } catch (error) {
      const mensaje = error instanceof ApiException ? error.message : "No se pudieron cargar los laboratorios";
      Toast.error(mensaje);
    }
  }

  async _pintarLista(laboratorios) {
    for (const badge of this._badges) {
      badge.destruir();
    }
    this._badges = [];
    this._contenedorLista.innerHTML = "";

    if (laboratorios.length === 0) {
      const vacio = document.createElement("p");
      vacio.className = "texto-marcador";
      vacio.textContent = "Aun no hay laboratorios registrados.";
      this._contenedorLista.appendChild(vacio);
      return;
    }

    for (const laboratorio of laboratorios) {
      const tarjeta = document.createElement("article");
      tarjeta.className = "laboratorio-tarjeta";

      const encabezado = document.createElement("div");
      encabezado.className = "laboratorio-tarjeta-encabezado";
      const titulo = document.createElement("h3");
      titulo.className = "laboratorio-tarjeta-titulo";
      titulo.textContent = `${laboratorio.nombre} - ${laboratorio.pabellon}, piso ${laboratorio.piso}`;
      encabezado.appendChild(titulo);

      const zonaAcciones = document.createElement("div");
      zonaAcciones.className = "laboratorio-tarjeta-item-acciones";

      const espacioEstado = document.createElement("span");
      zonaAcciones.appendChild(espacioEstado);
      this._badges.push(
        new StatusBadge(espacioEstado, {
          valor: laboratorio.estadoOperativo ? "OPERATIVO" : "EN_MANTENIMIENTO",
          tipo: "estadoEquipo",
        }),
      );

      const botonEstado = document.createElement("button");
      botonEstado.type = "button";
      botonEstado.className = `boton boton-sm ${laboratorio.estadoOperativo ? "boton-peligro" : "boton-secundario"}`;
      botonEstado.textContent = laboratorio.estadoOperativo ? "Pasar a mantenimiento" : "Marcar operativo";
      botonEstado.addEventListener("click", () => this._alternarEstadoOperativo(laboratorio));
      zonaAcciones.appendChild(botonEstado);

      const botonEditar = document.createElement("button");
      botonEditar.type = "button";
      botonEditar.className = "boton boton-secundario boton-sm";
      botonEditar.textContent = "Editar";
      botonEditar.addEventListener("click", () => this._entrarModoEdicion(laboratorio));
      zonaAcciones.appendChild(botonEditar);

      encabezado.appendChild(zonaAcciones);
      tarjeta.appendChild(encabezado);

      const listaEquipos = document.createElement("ul");
      tarjeta.appendChild(listaEquipos);

      const formularioEquipo = document.createElement("form");
      formularioEquipo.className = "laboratorio-tarjeta-form-equipo";
      const campoCodigo = document.createElement("input");
      campoCodigo.placeholder = "Codigo patrimonial";
      formularioEquipo.appendChild(campoCodigo);

      const campoTipo = document.createElement("input");
      campoTipo.placeholder = "Tipo de equipo";
      formularioEquipo.appendChild(campoTipo);

      const botonAgregar = document.createElement("button");
      botonAgregar.type = "submit";
      botonAgregar.className = "boton boton-fantasma boton-sm";
      botonAgregar.textContent = "Agregar equipo";
      formularioEquipo.appendChild(botonAgregar);
      tarjeta.appendChild(formularioEquipo);

      this._contenedorLista.appendChild(tarjeta);

      await this._cargarEquipos(laboratorio.idLaboratorio, listaEquipos);

      formularioEquipo.addEventListener("submit", async (evento) => {
        evento.preventDefault();
        try {
          const datos = new EquipoDTO(campoCodigo.value, campoTipo.value);
          await this.equipoService.registrar(laboratorio.idLaboratorio, datos);
          Toast.exito("Equipo registrado");
          formularioEquipo.reset();
          await this._cargarEquipos(laboratorio.idLaboratorio, listaEquipos);
        } catch (error) {
          const mensaje = error instanceof ApiException ? error.message : "No se pudo registrar el equipo";
          Toast.error(mensaje);
        }
      });
    }
  }

  async _cargarEquipos(idLaboratorio, listaEquipos) {
    try {
      const equipos = await this.equipoService.listarPorLaboratorio(idLaboratorio);
      listaEquipos.innerHTML = "";
      if (equipos.length === 0) {
        const vacio = document.createElement("li");
        vacio.className = "texto-tenue";
        vacio.textContent = "Sin equipos registrados";
        listaEquipos.appendChild(vacio);
      }
      for (const equipo of equipos) {
        const item = document.createElement("li");

        const info = document.createElement("span");
        info.textContent = `${equipo.codigoPatrimonial} - ${equipo.tipoEquipo}`;
        item.appendChild(info);

        const zonaDerecha = document.createElement("div");
        zonaDerecha.className = "laboratorio-tarjeta-item-acciones";

        const espacioEstado = document.createElement("span");
        zonaDerecha.appendChild(espacioEstado);
        this._badges.push(new StatusBadge(espacioEstado, { valor: equipo.estado, tipo: "estadoEquipo" }));

        const selectEstado = document.createElement("select");
        for (const estado of ESTADOS_EQUIPO) {
          const opcion = document.createElement("option");
          opcion.value = estado.valor;
          opcion.textContent = estado.texto;
          opcion.selected = estado.valor === equipo.estado;
          selectEstado.appendChild(opcion);
        }
        selectEstado.addEventListener("change", async () => {
          try {
            await this.equipoService.cambiarEstado(equipo.idEquipo, selectEstado.value);
            Toast.exito("Estado del equipo actualizado");
            await this._cargarEquipos(idLaboratorio, listaEquipos);
          } catch (error) {
            const mensaje = error instanceof ApiException ? error.message : "No se pudo cambiar el estado";
            Toast.error(mensaje);
          }
        });
        zonaDerecha.appendChild(selectEstado);
        item.appendChild(zonaDerecha);

        listaEquipos.appendChild(item);
      }
    } catch (error) {
      const mensaje = error instanceof ApiException ? error.message : "No se pudieron cargar los equipos";
      Toast.error(mensaje);
    }
  }
}
