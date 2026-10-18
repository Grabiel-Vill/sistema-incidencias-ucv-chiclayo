import { ApiServiceBase } from "./ApiServiceBase.js";

function aReporte(json) {
  return {
    idReporte: json.id_reporte,
    fechaGeneracion: json.fecha_generacion,
    kpisLaboratorios: json.kpis_laboratorios,
    frecuenciaFallas: json.frecuencia_fallas,
  };
}

export class ReporteService extends ApiServiceBase {
  constructor(httpClient) {
    super(httpClient, "/reportes");
  }

  async generar() {
    const json = await this._http.post(this._rutaBase);
    return aReporte(json);
  }

  async listarHistorial(limite = 10) {
    const json = await this._http.get(this._rutaBase, { limite });
    return json.map(aReporte);
  }

  exportar(idReporte, formato) {
    return this._http.descargarArchivo(`${this._rutaBase}/${idReporte}/exportar`, { formato });
  }
}
