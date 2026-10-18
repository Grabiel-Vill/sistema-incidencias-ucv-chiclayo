import { SessionStore } from "../state/SessionStore.js";
import { ApiException } from "./ApiException.js";

export class HttpClient {
  constructor(baseUrl = "", sessionStore = SessionStore) {
    this.baseUrl = baseUrl;
    this._sessionStore = sessionStore;
  }

  get(ruta, parametros = {}) {
    return this._solicitar("GET", ruta, { parametros });
  }

  post(ruta, cuerpo) {
    return this._solicitar("POST", ruta, { cuerpo });
  }

  patch(ruta, cuerpo) {
    return this._solicitar("PATCH", ruta, { cuerpo });
  }

  put(ruta, cuerpo) {
    return this._solicitar("PUT", ruta, { cuerpo });
  }

  async upload(ruta, formData) {
    const respuesta = await fetch(this.baseUrl + ruta, {
      method: "POST",
      headers: this._cabecerasAutenticacion(),
      body: formData,
    });
    return this._procesarRespuesta(respuesta);
  }

  async descargarArchivo(ruta, parametros = {}) {
    const respuesta = await fetch(this._construirUrl(ruta, parametros), {
      headers: this._cabecerasAutenticacion(),
    });
    if (!respuesta.ok) {
      await this._lanzarError(respuesta);
    }
    return respuesta.blob();
  }

  async _solicitar(metodo, ruta, { cuerpo, parametros } = {}) {
    const opciones = {
      method: metodo,
      headers: { "Content-Type": "application/json", ...this._cabecerasAutenticacion() },
    };
    if (cuerpo !== undefined) {
      opciones.body = JSON.stringify(cuerpo);
    }
    const respuesta = await fetch(this._construirUrl(ruta, parametros), opciones);
    return this._procesarRespuesta(respuesta);
  }

  _construirUrl(ruta, parametros = {}) {
    const origen = typeof window !== "undefined" ? window.location.origin : undefined;
    const url = new URL(this.baseUrl + ruta, origen);
    for (const [clave, valor] of Object.entries(parametros || {})) {
      if (valor !== undefined && valor !== null && valor !== "") {
        url.searchParams.set(clave, valor);
      }
    }
    return url.toString();
  }

  _cabecerasAutenticacion() {
    const token = this._sessionStore.obtenerToken();
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  async _procesarRespuesta(respuesta) {
    if (respuesta.status === 204) {
      return null;
    }
    if (!respuesta.ok) {
      await this._lanzarError(respuesta);
    }
    return respuesta.json();
  }

  async _lanzarError(respuesta) {
    let cuerpo = { error: "ERROR_DESCONOCIDO", mensaje: `Error HTTP ${respuesta.status}` };
    try {
      cuerpo = await respuesta.json();
    } catch {
      // la respuesta no trae JSON (ej. caida de red antes de llegar al backend)
    }
    throw new ApiException(cuerpo.error, cuerpo.mensaje, respuesta.status);
  }
}
