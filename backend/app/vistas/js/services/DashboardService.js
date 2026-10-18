import { MetricasDTO } from "../models/MetricasDTO.js";
import { ApiServiceBase } from "./ApiServiceBase.js";

export class DashboardService extends ApiServiceBase {
  constructor(httpClient) {
    super(httpClient, "/dashboard");
  }

  async obtenerMetricas() {
    const json = await this._http.get(`${this._rutaBase}/metricas`);
    return MetricasDTO.fromJSON(json);
  }

  exportarReporte(formato) {
    return this._http.descargarArchivo(`${this._rutaBase}/reporte`, { formato });
  }
}
