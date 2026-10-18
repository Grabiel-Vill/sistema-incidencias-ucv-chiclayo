import { UsuarioDTO } from "../models/UsuarioDTO.js";

const CLAVE_TOKEN = "sistema_incidencias_token";
const CLAVE_USUARIO = "sistema_incidencias_usuario";

class SessionStoreClase {
  constructor(almacenamiento = localStorage) {
    this._almacenamiento = almacenamiento;
    this._token = this._almacenamiento.getItem(CLAVE_TOKEN) || null;
    const usuarioGuardado = this._almacenamiento.getItem(CLAVE_USUARIO);
    this._usuario = usuarioGuardado ? UsuarioDTO.fromJSON(JSON.parse(usuarioGuardado)) : null;
    this._listeners = new Set();
  }

  iniciarSesion(token, usuario) {
    this._token = token;
    this._usuario = usuario;
    this._almacenamiento.setItem(CLAVE_TOKEN, token);
    if (usuario) {
      this._almacenamiento.setItem(CLAVE_USUARIO, JSON.stringify(usuario));
    } else {
      this._almacenamiento.removeItem(CLAVE_USUARIO);
    }
    this._notificar();
  }

  cerrarSesion() {
    this._token = null;
    this._usuario = null;
    this._almacenamiento.removeItem(CLAVE_TOKEN);
    this._almacenamiento.removeItem(CLAVE_USUARIO);
    this._notificar();
  }

  obtenerToken() {
    return this._token;
  }

  obtenerUsuario() {
    return this._usuario;
  }

  estaAutenticado() {
    return this._token !== null && this._usuario !== null;
  }

  tieneRol(...roles) {
    return this._usuario !== null && roles.includes(this._usuario.rol);
  }

  suscribir(callback) {
    this._listeners.add(callback);
    return () => this._listeners.delete(callback);
  }

  _notificar() {
    for (const callback of this._listeners) {
      callback(this._usuario);
    }
  }
}

export const SessionStore = new SessionStoreClase();
export { SessionStoreClase };
