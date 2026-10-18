import { Loader } from "../components/Loader.js";
import { Modal } from "../components/Modal.js";
import { Toast } from "../components/Toast.js";
import { UsuarioService } from "../services/UsuarioService.js";
import { ApiException } from "../utils/ApiException.js";
import { Validators } from "../utils/Validators.js";
import { PageControllerBase } from "./PageControllerBase.js";

const ROLES = [
  { valor: "DOCENTE", texto: "Docente" },
  { valor: "TECNICO", texto: "Tecnico" },
  { valor: "ADMINISTRADOR", texto: "Administrador" },
];

export class AdminUsuariosController extends PageControllerBase {
  constructor(contenedor) {
    super(contenedor, ["ADMINISTRADOR"], "Usuarios");
  }

  inicializar() {
    this.usuarioService = new UsuarioService(this.http);
    this.modal = new Modal(document.getElementById("contenedor-modal"));
    this._montarFormulario();
    this._contenedorTabla = document.getElementById("contenedor-tabla-usuarios");
    this._cargarUsuarios();
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
    const contenedor = document.getElementById("contenedor-formulario-usuario");
    contenedor.innerHTML = "";

    const formulario = document.createElement("form");
    formulario.className = "formulario-grid";

    const campoCodigo = document.createElement("input");
    campoCodigo.placeholder = "D001";
    formulario.appendChild(this._campo("Codigo UCV", campoCodigo));

    const campoNombre = document.createElement("input");
    formulario.appendChild(this._campo("Nombre", campoNombre));

    const campoApellido = document.createElement("input");
    formulario.appendChild(this._campo("Apellido", campoApellido));

    const campoEmail = document.createElement("input");
    campoEmail.type = "email";
    formulario.appendChild(this._campo("Correo", campoEmail));

    const campoPassword = document.createElement("input");
    campoPassword.type = "password";
    formulario.appendChild(this._campo("Contrasena temporal", campoPassword));

    const selectRol = document.createElement("select");
    for (const rol of ROLES) {
      const opcion = document.createElement("option");
      opcion.value = rol.valor;
      opcion.textContent = rol.texto;
      selectRol.appendChild(opcion);
    }
    formulario.appendChild(this._campo("Rol", selectRol));

    const campoEspecialidad = document.createElement("input");
    const grupoEspecialidad = this._campo("Especialidad (solo tecnico)", campoEspecialidad);
    grupoEspecialidad.classList.add("oculto");
    formulario.appendChild(grupoEspecialidad);

    selectRol.addEventListener("change", () => {
      grupoEspecialidad.classList.toggle("oculto", selectRol.value !== "TECNICO");
    });

    const botonEnviar = document.createElement("button");
    botonEnviar.type = "submit";
    botonEnviar.className = "boton boton-primario campo-formulario-ancho";
    botonEnviar.textContent = "Registrar usuario";
    formulario.appendChild(botonEnviar);

    contenedor.appendChild(formulario);

    formulario.addEventListener("submit", async (evento) => {
      evento.preventDefault();
      try {
        if (!Validators.esNoVacio(campoCodigo.value) || !Validators.esNoVacio(campoNombre.value)) {
          throw new ApiException("VALIDACION", "Completa los campos obligatorios");
        }
        await this.usuarioService.registrar({
          codigoUcv: campoCodigo.value,
          nombre: campoNombre.value,
          apellido: campoApellido.value,
          email: campoEmail.value,
          password: campoPassword.value,
          rol: selectRol.value,
          especialidad: selectRol.value === "TECNICO" ? campoEspecialidad.value : null,
        });
        Toast.exito("Usuario registrado");
        formulario.reset();
        grupoEspecialidad.classList.add("oculto");
        this._cargarUsuarios();
      } catch (error) {
        const mensaje = error instanceof ApiException ? error.message : "No se pudo registrar el usuario";
        Toast.error(mensaje);
      }
    });
  }

  async _cargarUsuarios() {
    new Loader(this._contenedorTabla, { texto: "Cargando usuarios..." });
    try {
      const usuarios = await this.usuarioService.listar();
      this._pintarTabla(usuarios);
    } catch (error) {
      const mensaje = error instanceof ApiException ? error.message : "No se pudieron cargar los usuarios";
      Toast.error(mensaje);
    }
  }

  _pintarTabla(usuarios) {
    this._contenedorTabla.innerHTML = "";

    if (usuarios.length === 0) {
      const vacio = document.createElement("p");
      vacio.className = "texto-marcador";
      vacio.textContent = "Aun no hay usuarios registrados.";
      this._contenedorTabla.appendChild(vacio);
      return;
    }

    const envoltorio = document.createElement("div");
    envoltorio.className = "tabla-incidencias-envoltorio";

    const tabla = document.createElement("table");
    const encabezado = document.createElement("thead");
    encabezado.innerHTML =
      "<tr><th>Nombre</th><th>Email</th><th>Rol</th><th>Especialidad</th><th>Estado</th><th></th></tr>";
    tabla.appendChild(encabezado);

    const cuerpo = document.createElement("tbody");
    for (const usuario of usuarios) {
      const fila = document.createElement("tr");

      const celdaNombre = document.createElement("td");
      celdaNombre.textContent = usuario.nombreCompleto;
      fila.appendChild(celdaNombre);

      const celdaEmail = document.createElement("td");
      celdaEmail.textContent = usuario.email;
      fila.appendChild(celdaEmail);

      const celdaRol = document.createElement("td");
      celdaRol.textContent = usuario.rol;
      fila.appendChild(celdaRol);

      const celdaEspecialidad = document.createElement("td");
      celdaEspecialidad.textContent = usuario.especialidad || "-";
      fila.appendChild(celdaEspecialidad);

      const celdaEstado = document.createElement("td");
      celdaEstado.textContent = usuario.estado ? "Activo" : "Inactivo";
      fila.appendChild(celdaEstado);

      const celdaAcciones = document.createElement("td");
      celdaAcciones.className = "tabla-incidencias-acciones";

      const botonEditar = document.createElement("button");
      botonEditar.type = "button";
      botonEditar.className = "boton boton-fantasma boton-sm";
      botonEditar.textContent = "Editar";
      botonEditar.addEventListener("click", () => this._abrirEdicion(usuario));
      celdaAcciones.appendChild(botonEditar);

      const botonReset = document.createElement("button");
      botonReset.type = "button";
      botonReset.className = "boton boton-secundario boton-sm";
      botonReset.textContent = "Restablecer password";
      botonReset.addEventListener("click", () => this._restablecerPassword(usuario));
      celdaAcciones.appendChild(botonReset);

      const botonEstado = document.createElement("button");
      botonEstado.type = "button";
      botonEstado.className = `boton boton-sm ${usuario.estado ? "boton-peligro" : "boton-secundario"}`;
      botonEstado.textContent = usuario.estado ? "Desactivar" : "Activar";
      botonEstado.addEventListener("click", () => this._cambiarEstado(usuario));
      celdaAcciones.appendChild(botonEstado);

      fila.appendChild(celdaAcciones);
      cuerpo.appendChild(fila);
    }
    tabla.appendChild(cuerpo);
    envoltorio.appendChild(tabla);
    this._contenedorTabla.appendChild(envoltorio);
  }

  _abrirEdicion(usuario) {
    const mostrarEspecialidad = usuario.rol === "TECNICO";
    this.modal.abrir(`
      <h3>Editar usuario</h3>
      <form class="formulario-edicion-usuario">
        <div class="campo-formulario">
          <label>Codigo UCV</label>
          <input class="campo-edicion-codigo" value="${usuario.codigoUcv}" />
        </div>
        <div class="campo-formulario">
          <label>Nombre</label>
          <input class="campo-edicion-nombre" value="${usuario.nombre}" />
        </div>
        <div class="campo-formulario">
          <label>Apellido</label>
          <input class="campo-edicion-apellido" value="${usuario.apellido}" />
        </div>
        <div class="campo-formulario">
          <label>Correo</label>
          <input type="email" class="campo-edicion-email" value="${usuario.email}" />
        </div>
        <div class="campo-formulario ${mostrarEspecialidad ? "" : "oculto"}">
          <label>Especialidad</label>
          <input class="campo-edicion-especialidad" value="${usuario.especialidad || ""}" />
        </div>
        <p class="texto-tenue">El rol (${usuario.rol}) no se puede cambiar desde aqui.</p>
        <div class="modal-acciones">
          <button type="button" class="boton boton-secundario" data-accion="cancelar">Cancelar</button>
          <button type="submit" class="boton boton-primario">Guardar cambios</button>
        </div>
      </form>
    `);

    const caja = this.modal.contenedor;
    caja.querySelector('[data-accion="cancelar"]')?.addEventListener("click", () => this.modal.cerrar(), {
      once: true,
    });
    caja.querySelector(".formulario-edicion-usuario").addEventListener("submit", async (evento) => {
      evento.preventDefault();
      try {
        await this.usuarioService.editar(usuario.idUsuario, {
          codigoUcv: caja.querySelector(".campo-edicion-codigo").value,
          nombre: caja.querySelector(".campo-edicion-nombre").value,
          apellido: caja.querySelector(".campo-edicion-apellido").value,
          email: caja.querySelector(".campo-edicion-email").value,
          especialidad: mostrarEspecialidad ? caja.querySelector(".campo-edicion-especialidad").value : null,
        });
        Toast.exito("Usuario actualizado");
        this.modal.cerrar();
        this._cargarUsuarios();
      } catch (error) {
        const mensaje = error instanceof ApiException ? error.message : "No se pudo actualizar el usuario";
        Toast.error(mensaje);
      }
    });
  }

  async _restablecerPassword(usuario) {
    try {
      const passwordTemporal = await this.usuarioService.restablecerPassword(usuario.idUsuario);
      this.modal.abrir(`
        <h3>Contrasena restablecida</h3>
        <p class="modal-mensaje">Nueva contrasena temporal para <strong>${usuario.nombreCompleto}</strong>:</p>
        <p class="password-temporal-destacada">${passwordTemporal}</p>
        <p class="texto-tenue">Comunicasela al usuario ahora: no se volvera a mostrar.</p>
        <div class="modal-acciones">
          <button type="button" class="boton boton-primario" data-accion="cerrar">Entendido</button>
        </div>
      `);
      this.modal.contenedor
        .querySelector('[data-accion="cerrar"]')
        ?.addEventListener("click", () => this.modal.cerrar(), { once: true });
    } catch (error) {
      const mensaje = error instanceof ApiException ? error.message : "No se pudo restablecer la contrasena";
      Toast.error(mensaje);
    }
  }

  async _cambiarEstado(usuario) {
    try {
      await this.usuarioService.cambiarEstado(usuario.idUsuario, !usuario.estado);
      Toast.exito(`Usuario ${usuario.nombreCompleto} actualizado`);
      this._cargarUsuarios();
    } catch (error) {
      const mensaje = error instanceof ApiException ? error.message : "No se pudo cambiar el estado";
      Toast.error(mensaje);
    }
  }
}
