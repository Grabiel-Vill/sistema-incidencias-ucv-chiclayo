import { NotificacionDTO } from "../models/NotificacionDTO.js";
import { ApiServiceBase } from "./ApiServiceBase.js";

export class NotificacionService extends ApiServiceBase {
  constructor(httpClient) {
    super(httpClient, "/notificaciones");
  }

  async listar(soloNoLeidas = false) {
    const json = await this._http.get(this._rutaBase, { solo_no_leidas: soloNoLeidas });
    return json.map(NotificacionDTO.fromJSON);
  }

  async marcarLeido(idNotificacion) {
    const json = await this._http.patch(`${this._rutaBase}/${idNotificacion}/leido`);
    return NotificacionDTO.fromJSON(json);
  }
}
