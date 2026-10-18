import { IncidenciaRespuestaDTO } from "../models/IncidenciaRespuestaDTO.js";
import { ApiServiceBase } from "./ApiServiceBase.js";

export class IncidenciaService extends ApiServiceBase {
  constructor(httpClient) {
    super(httpClient, "/incidencias");
  }

  async registrar(incidenciaDTO) {
    const json = await this._http.post(this._rutaBase, incidenciaDTO.toJSON());
    return IncidenciaRespuestaDTO.fromJSON(json);
  }

  async obtenerPorId(idIncidencia) {
    const json = await this._http.get(`${this._rutaBase}/${idIncidencia}`);
    return IncidenciaRespuestaDTO.fromJSON(json);
  }

  async listarMias() {
    const json = await this._http.get(`${this._rutaBase}/mias`);
    return json.map(IncidenciaRespuestaDTO.fromJSON);
  }

  async listarConFiltro(filtro = {}) {
    const parametros = {
      id_laboratorio: filtro.idLaboratorio,
      tipo_falla: filtro.tipoFalla,
      estado: filtro.estado,
      id_tecnico: filtro.idTecnico,
      fecha_desde: filtro.fechaDesde,
      fecha_hasta: filtro.fechaHasta,
    };
    const json = await this._http.get(this._rutaBase, parametros);
    return json.map(IncidenciaRespuestaDTO.fromJSON);
  }

  async asignarTecnico(idIncidencia, idTecnico, prioridad = "MEDIA") {
    const json = await this._http.post(`${this._rutaBase}/${idIncidencia}/asignar`, {
      id_tecnico: idTecnico,
      prioridad,
    });
    return IncidenciaRespuestaDTO.fromJSON(json);
  }

  async atender(idIncidencia) {
    const json = await this._http.post(`${this._rutaBase}/${idIncidencia}/atender`);
    return IncidenciaRespuestaDTO.fromJSON(json);
  }

  async cambiarEstado(idIncidencia, estado) {
    const json = await this._http.patch(`${this._rutaBase}/${idIncidencia}/estado`, { estado });
    return IncidenciaRespuestaDTO.fromJSON(json);
  }

  async priorizar(idIncidencia, prioridad) {
    const json = await this._http.patch(`${this._rutaBase}/${idIncidencia}/prioridad`, { prioridad });
    return IncidenciaRespuestaDTO.fromJSON(json);
  }

  async obtenerCatalogo() {
    return this._http.get(`${this._rutaBase}/catalogo`);
  }

  async obtenerMisMetricas() {
    return this._http.get(`${this._rutaBase}/mis-metricas`);
  }

  async obtenerCargaTecnicos() {
    return this._http.get(`${this._rutaBase}/tecnicos/carga`);
  }

  async calificar(idIncidencia, estrellas, comentario) {
    return this._http.post(`${this._rutaBase}/${idIncidencia}/calificacion`, { estrellas, comentario });
  }
}
