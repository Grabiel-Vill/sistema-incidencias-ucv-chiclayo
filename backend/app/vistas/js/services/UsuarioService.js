import { UsuarioDTO } from "../models/UsuarioDTO.js";
import { ApiServiceBase } from "./ApiServiceBase.js";

export class UsuarioService extends ApiServiceBase {
  constructor(httpClient) {
    super(httpClient, "/usuarios");
  }

  async registrar({ codigoUcv, nombre, apellido, email, password, rol, especialidad = null }) {
    const json = await this._http.post(this._rutaBase, {
      codigo_ucv: codigoUcv,
      nombre,
      apellido,
      email,
      password,
      rol,
      especialidad,
    });
    return UsuarioDTO.fromJSON(json);
  }

  async cambiarEstado(idUsuario, activo) {
    const json = await this._http.patch(`${this._rutaBase}/${idUsuario}/estado`, { activo });
    return UsuarioDTO.fromJSON(json);
  }

  async listar() {
    const json = await this._http.get(this._rutaBase);
    return json.map(UsuarioDTO.fromJSON);
  }

  async editar(idUsuario, { codigoUcv, nombre, apellido, email, especialidad = null }) {
    const json = await this._http.put(`${this._rutaBase}/${idUsuario}`, {
      codigo_ucv: codigoUcv,
      nombre,
      apellido,
      email,
      especialidad,
    });
    return UsuarioDTO.fromJSON(json);
  }

  async restablecerPassword(idUsuario) {
    const json = await this._http.post(`${this._rutaBase}/${idUsuario}/restablecer-password`);
    return json.password_temporal;
  }
}
