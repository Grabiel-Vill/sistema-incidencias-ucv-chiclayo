import { LaboratorioDTO } from "../models/LaboratorioDTO.js";
import { ApiServiceBase } from "./ApiServiceBase.js";

export class LaboratorioService extends ApiServiceBase {
  constructor(httpClient) {
    super(httpClient, "/laboratorios");
  }

  async registrar(laboratorioDTO) {
    const json = await this._http.post(this._rutaBase, laboratorioDTO.toJSON());
    return LaboratorioDTO.fromJSON(json);
  }

  async editar(idLaboratorio, laboratorioDTO) {
    const json = await this._http.put(`${this._rutaBase}/${idLaboratorio}`, laboratorioDTO.toJSON());
    return LaboratorioDTO.fromJSON(json);
  }

  async listar() {
    const json = await this._http.get(this._rutaBase);
    return json.map(LaboratorioDTO.fromJSON);
  }

  obtenerHistorial(idLaboratorio) {
    return this._http.get(`${this._rutaBase}/${idLaboratorio}/historial`);
  }
}
