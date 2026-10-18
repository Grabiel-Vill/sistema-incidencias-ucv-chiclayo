export class IncidenciaRespuestaDTO {
  constructor(
    idIncidencia,
    codigoTicket,
    descripcion,
    tipoFalla,
    estado,
    prioridad,
    fechaCreacion,
    fechaAtencion,
    fechaResolucion,
    tecnicoAsignado,
    notasPublicas,
    subcategoria,
    idLaboratorio,
    laboratorio,
    idTecnicoAsignado,
    idDocente,
    docente,
    fechaHoraApertura,
    tipoRequerimiento,
    idEquipo,
    equipo,
    calificada,
  ) {
    this.idIncidencia = idIncidencia;
    this.codigoTicket = codigoTicket;
    this.descripcion = descripcion;
    this.tipoFalla = tipoFalla;
    this.estado = estado;
    this.prioridad = prioridad;
    this.fechaCreacion = fechaCreacion;
    this.fechaAtencion = fechaAtencion;
    this.fechaResolucion = fechaResolucion;
    this.tecnicoAsignado = tecnicoAsignado;
    this.notasPublicas = notasPublicas;
    this.subcategoria = subcategoria;
    this.idLaboratorio = idLaboratorio;
    this.laboratorio = laboratorio;
    this.idTecnicoAsignado = idTecnicoAsignado;
    this.idDocente = idDocente;
    this.docente = docente;
    this.fechaHoraApertura = fechaHoraApertura;
    this.tipoRequerimiento = tipoRequerimiento;
    this.idEquipo = idEquipo;
    this.equipo = equipo;
    this.calificada = calificada;
  }

  static fromJSON(json) {
    return new IncidenciaRespuestaDTO(
      json.id_incidencia,
      json.codigo_ticket,
      json.descripcion,
      json.tipo_falla,
      json.estado,
      json.prioridad,
      json.fecha_creacion,
      json.fecha_atencion,
      json.fecha_resolucion,
      json.tecnico_asignado,
      json.notas_publicas || [],
      json.subcategoria,
      json.id_laboratorio,
      json.laboratorio,
      json.id_tecnico_asignado,
      json.id_docente,
      json.docente,
      json.fecha_hora_apertura,
      json.tipo_requerimiento,
      json.id_equipo,
      json.equipo,
      Boolean(json.calificada),
    );
  }
}
