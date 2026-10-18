import { ApiException } from "../utils/ApiException.js";
import { ComponentBase } from "./ComponentBase.js";
import { Icon } from "./Icon.js";

const CLAVE_ABIERTO = "sistema_incidencias_chatbot_abierto";

export class ChatbotWidget extends ComponentBase {
  // props: { chatbotService, laboratorioService, onCrearTicketSugerido? }
  render() {
    this.contenedor.innerHTML = "";
    this.contenedor.className = "widget-chatbot";
    this._enviando = false;

    this._lanzador = document.createElement("button");
    this._lanzador.type = "button";
    this._lanzador.className = "widget-chatbot-lanzador";
    this._lanzador.appendChild(Icon.elemento("chat", { tamano: 23, color: "#ffffff" }));
    this.contenedor.appendChild(this._lanzador);
    this._escuchar(this._lanzador, "click", () => this._abrir());

    this._panel = document.createElement("div");
    this._panel.className = "widget-chatbot-panel widget-chatbot-panel-oculto";
    this.contenedor.appendChild(this._panel);

    this._panel.appendChild(this._crearEncabezado());

    const barraLaboratorio = document.createElement("div");
    barraLaboratorio.className = "widget-chatbot-laboratorio";
    const etiquetaLab = document.createElement("label");
    etiquetaLab.textContent = "Laboratorio";
    barraLaboratorio.appendChild(etiquetaLab);
    this._selectLaboratorio = document.createElement("select");
    barraLaboratorio.appendChild(this._selectLaboratorio);
    this._panel.appendChild(barraLaboratorio);

    this._historial = document.createElement("div");
    this._historial.className = "widget-chatbot-historial";
    this._panel.appendChild(this._historial);

    this._indicadorEscribiendo = document.createElement("div");
    this._indicadorEscribiendo.className = "widget-chatbot-escribiendo";
    this._indicadorEscribiendo.innerHTML = "<span></span><span></span><span></span>";

    this._panel.appendChild(this._crearFormulario());

    this._agregarMensaje("Hola, soy el asistente virtual de soporte. Cuentame que problema tienes y te ayudo.", "asistente");
    this._cargarLaboratorios();

    if (localStorage.getItem(CLAVE_ABIERTO) === "1") {
      this._abrir();
    }
  }

  _crearEncabezado() {
    const encabezado = document.createElement("div");
    encabezado.className = "widget-chatbot-encabezado";

    const avatarBot = document.createElement("span");
    avatarBot.className = "widget-chatbot-avatar-bot";
    avatarBot.appendChild(Icon.elemento("chat", { tamano: 15, color: "#ffffff" }));
    encabezado.appendChild(avatarBot);

    const textos = document.createElement("div");
    textos.className = "widget-chatbot-encabezado-textos";
    const titulo = document.createElement("p");
    titulo.className = "widget-chatbot-titulo";
    titulo.textContent = "Asistente Virtual";
    textos.appendChild(titulo);
    const subtitulo = document.createElement("p");
    subtitulo.className = "widget-chatbot-subtitulo";
    subtitulo.innerHTML = '<span class="widget-chatbot-punto-activo"></span>Soporte tecnico Nivel 1';
    textos.appendChild(subtitulo);
    encabezado.appendChild(textos);

    const botonCerrar = document.createElement("button");
    botonCerrar.type = "button";
    botonCerrar.className = "widget-chatbot-boton-cerrar";
    botonCerrar.appendChild(Icon.elemento("cerrar", { tamano: 16, color: "#ffffff" }));
    this._escuchar(botonCerrar, "click", () => this._cerrar());
    encabezado.appendChild(botonCerrar);

    return encabezado;
  }

  _crearFormulario() {
    const formulario = document.createElement("form");
    formulario.className = "widget-chatbot-formulario";

    this._campoMensaje = document.createElement("input");
    this._campoMensaje.type = "text";
    this._campoMensaje.placeholder = "Escribe tu consulta...";
    this._campoMensaje.autocomplete = "off";
    formulario.appendChild(this._campoMensaje);

    this._botonEnviar = document.createElement("button");
    this._botonEnviar.type = "submit";
    this._botonEnviar.className = "widget-chatbot-boton-enviar";
    this._botonEnviar.appendChild(Icon.elemento("enviar", { tamano: 16, color: "#ffffff" }));
    formulario.appendChild(this._botonEnviar);

    this._escuchar(formulario, "submit", (evento) => {
      evento.preventDefault();
      this._enviarMensaje();
    });

    return formulario;
  }

  async _cargarLaboratorios() {
    const laboratorioService = this.props.laboratorioService;
    if (!laboratorioService) {
      return;
    }
    try {
      const laboratorios = await laboratorioService.listar();
      this._selectLaboratorio.innerHTML = "";
      for (const laboratorio of laboratorios) {
        const opcion = document.createElement("option");
        opcion.value = laboratorio.idLaboratorio;
        opcion.textContent = laboratorio.nombre;
        this._selectLaboratorio.appendChild(opcion);
      }
    } catch {
      // si falla la carga de laboratorios el chat sigue usable; se valida al enviar
    }
  }

  async _enviarMensaje() {
    const mensaje = this._campoMensaje.value.trim();
    if (!mensaje || this._enviando) {
      return;
    }

    const idLaboratorio = Number(this._selectLaboratorio.value) || null;
    if (!idLaboratorio) {
      this._agregarMensaje("Selecciona un laboratorio antes de continuar.", "asistente");
      return;
    }

    this._agregarMensaje(mensaje, "propio");
    this._campoMensaje.value = "";
    this._fijarCargando(true);

    try {
      const respuesta = await this.props.chatbotService.procesarMensaje(mensaje, idLaboratorio);
      this._agregarMensaje(respuesta.respuesta, "asistente");
      for (const sugerencia of respuesta.sugerencias) {
        this._agregarMensaje(sugerencia, "sugerencia");
      }
      if (respuesta.requiereAtencionFisica && respuesta.sugerenciaTicket) {
        this._agregarBotonCrearTicket(respuesta.sugerenciaTicket);
      }
    } catch (error) {
      const mensajeError =
        error instanceof ApiException ? error.message : "No se pudo contactar al asistente. Intenta de nuevo.";
      this._agregarMensaje(mensajeError, "error");
    } finally {
      this._fijarCargando(false);
    }
  }

  _fijarCargando(cargando) {
    this._enviando = cargando;
    this._campoMensaje.disabled = cargando;
    this._botonEnviar.disabled = cargando;
    if (cargando) {
      this._historial.appendChild(this._indicadorEscribiendo);
    } else if (this._indicadorEscribiendo.parentElement) {
      this._indicadorEscribiendo.remove();
    }
    this._desplazarAbajo();
    if (!cargando) {
      this._campoMensaje.focus();
    }
  }

  _agregarMensaje(texto, variante) {
    const fila = document.createElement("div");
    fila.className = `widget-chatbot-fila widget-chatbot-fila-${variante === "propio" ? "propio" : "otro"}`;

    if (variante !== "propio") {
      const avatar = document.createElement("span");
      avatar.className = "widget-chatbot-avatar-mini";
      avatar.appendChild(Icon.elemento("chat", { tamano: 12, color: "#ffffff" }));
      fila.appendChild(avatar);
    }

    const burbuja = document.createElement("div");
    burbuja.className = `widget-chatbot-burbuja widget-chatbot-burbuja-${variante}`;
    burbuja.textContent = texto;
    fila.appendChild(burbuja);

    this._historial.appendChild(fila);
    this._desplazarAbajo();
  }

  _desplazarAbajo() {
    this._historial.scrollTop = this._historial.scrollHeight;
  }

  _agregarBotonCrearTicket(sugerenciaTicket) {
    const fila = document.createElement("div");
    fila.className = "widget-chatbot-fila widget-chatbot-fila-otro";

    const avatar = document.createElement("span");
    avatar.className = "widget-chatbot-avatar-mini";
    avatar.appendChild(Icon.elemento("chat", { tamano: 12, color: "#ffffff" }));
    fila.appendChild(avatar);

    const burbuja = document.createElement("div");
    burbuja.className = "widget-chatbot-burbuja widget-chatbot-burbuja-ticket";

    const texto = document.createElement("p");
    texto.textContent = "La falla requiere atencion tecnica presencial.";
    burbuja.appendChild(texto);

    const boton = document.createElement("button");
    boton.type = "button";
    boton.className = "boton boton-primario boton-sm widget-chatbot-boton-crear-ticket";
    boton.textContent = "Crear ticket con estos datos";
    this._escuchar(boton, "click", () => {
      if (typeof this.props.onCrearTicketSugerido === "function") {
        this.props.onCrearTicketSugerido(sugerenciaTicket);
      }
      this._cerrar();
    });
    burbuja.appendChild(boton);

    fila.appendChild(burbuja);
    this._historial.appendChild(fila);
    this._desplazarAbajo();
  }

  _abrir() {
    this._panel.classList.remove("widget-chatbot-panel-oculto");
    this._lanzador.classList.add("widget-chatbot-lanzador-oculto");
    this._campoMensaje.focus();
    localStorage.setItem(CLAVE_ABIERTO, "1");
  }

  _cerrar() {
    this._panel.classList.add("widget-chatbot-panel-oculto");
    this._lanzador.classList.remove("widget-chatbot-lanzador-oculto");
    localStorage.setItem(CLAVE_ABIERTO, "0");
  }
}
