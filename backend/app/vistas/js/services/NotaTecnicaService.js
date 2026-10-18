import { NotaTecnicaDTO } from "../models/NotaTecnicaDTO.js";
import { ApiServiceBase } from "./ApiServiceBase.js";

export class NotaTecnicaService extends ApiServiceBase {
  constructor(httpClient) {
    super(httpClient, "/incidencias");
  }

  async agregar(idIncidencia, notaTecnicaDTO) {
    const json = await this._http.post(`${this._rutaBase}/${idIncidencia}/notas`, notaTecnicaDTO.toJSON());
    return NotaTecnicaDTO.fromJSON(json);
  }

  async listar(idIncidencia) {
    const json = await this._http.get(`${this._rutaBase}/${idIncidencia}/notas`);
    return json.map(NotaTecnicaDTO.fromJSON);
  }
}
