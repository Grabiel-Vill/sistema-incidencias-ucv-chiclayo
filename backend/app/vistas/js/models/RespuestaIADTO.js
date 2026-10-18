export class RespuestaIADTO {
  constructor(respuesta, sugerencias = [], requiereAtencionFisica = false, sugerenciaTicket = null) {
    this.respuesta = respuesta;
    this.sugerencias = sugerencias;
    this.requiereAtencionFisica = requiereAtencionFisica;
    this.sugerenciaTicket = sugerenciaTicket;
  }

  static fromJSON(json) {
    const sugerencia = json.sugerencia_ticket
      ? {
          idLaboratorio: json.sugerencia_ticket.id_laboratorio,
          categoria: json.sugerencia_ticket.categoria,
          tipoFalla: json.sugerencia_ticket.tipo_falla,
          descripcion: json.sugerencia_ticket.descripcion,
        }
      : null;
    return new RespuestaIADTO(json.respuesta, json.sugerencias || [], Boolean(json.requiere_atencion_fisica), sugerencia);
  }
}
