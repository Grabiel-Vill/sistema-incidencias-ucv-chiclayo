export class DiagnosticoDTO {
  constructor(tipoFalla, diagnostico, prioridad) {
    this.tipoFalla = tipoFalla;
    this.diagnostico = diagnostico;
    this.prioridad = prioridad;
  }

  static fromJSON(json) {
    return new DiagnosticoDTO(json.tipo_falla, json.diagnostico, json.prioridad);
  }
}
