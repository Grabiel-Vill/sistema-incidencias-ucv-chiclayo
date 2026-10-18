export class MetricasDTO {
  constructor(
    kpisLaboratorios,
    frecuenciaFallas,
    equiposCriticos = [],
    puntualidadApertura = null,
    evaluacionPromedioTecnicos = null,
  ) {
    this.kpisLaboratorios = kpisLaboratorios;
    this.frecuenciaFallas = frecuenciaFallas;
    this.equiposCriticos = equiposCriticos;
    this.puntualidadApertura = puntualidadApertura;
    this.evaluacionPromedioTecnicos = evaluacionPromedioTecnicos;
  }

  static fromJSON(json) {
    return new MetricasDTO(
      json.kpis_laboratorios,
      json.frecuencia_fallas,
      json.equipos_criticos || [],
      json.puntualidad_apertura,
      json.evaluacion_promedio_tecnicos,
    );
  }
}
