import { EquipoDTO } from "../models/EquipoDTO.js";
import { ApiServiceBase } from "./ApiServiceBase.js";

export class EquipoService extends ApiServiceBase {
  constructor(httpClient) {
    super(httpClient, ""); // el EquipoController del backend no usa un prefijo unico
  }

  async registrar(idLaboratorio, equipoDTO) {
    const json = await this._http.post(`/laboratorios/${idLaboratorio}/equipos`, equipoDTO.toJSON());
    return EquipoDTO.fromJSON(json);
  }

  async listarPorLaboratorio(idLaboratorio) {
    const json = await this._http.get(`/laboratorios/${idLaboratorio}/equipos`);
    return json.map(EquipoDTO.fromJSON);
  }

  async cambiarEstado(idEquipo, estado) {
    const json = await this._http.patch(`/equipos/${idEquipo}/estado`, { estado });
    return EquipoDTO.fromJSON(json);
  }
}
