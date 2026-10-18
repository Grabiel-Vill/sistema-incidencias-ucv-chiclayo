import { ApiServiceBase } from "./ApiServiceBase.js";

export class EvidenciaService extends ApiServiceBase {
  constructor(httpClient) {
    super(httpClient, "/incidencias");
  }

  async subir(idIncidencia, archivo) {
    const formData = new FormData();
    formData.append("archivo", archivo);
    const json = await this._http.upload(`${this._rutaBase}/${idIncidencia}/evidencias`, formData);
    return { idEvidencia: json.id_evidencia, urlImagen: json.url_imagen };
  }

  async listar(idIncidencia) {
    const json = await this._http.get(`${this._rutaBase}/${idIncidencia}/evidencias`);
    return json.map((e) => ({ idEvidencia: e.id_evidencia, urlImagen: e.url_imagen }));
  }
}
