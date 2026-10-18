export class NotificacionDTO {
  constructor(idNotificacion, mensaje, tipo, fecha, leido, prioridad = null) {
    this.idNotificacion = idNotificacion;
    this.mensaje = mensaje;
    this.tipo = tipo;
    this.fecha = fecha;
    this.leido = leido;
    this.prioridad = prioridad;
  }

  static fromJSON(json) {
    return new NotificacionDTO(
      json.id_notificacion,
      json.mensaje,
      json.tipo,
      json.fecha,
      json.leido,
      json.prioridad || null,
    );
  }
}
