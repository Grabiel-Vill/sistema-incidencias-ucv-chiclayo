export class NotificationStore {
  constructor(notificacionService) {
    this._notificacionService = notificacionService;
    this._notificaciones = [];
    this._listeners = new Set();
    this._intervaloId = null;
  }

  async cargar() {
    this._notificaciones = await this._notificacionService.listar();
    this._notificar();
    return this._notificaciones;
  }

  async marcarLeido(idNotificacion) {
    const actualizada = await this._notificacionService.marcarLeido(idNotificacion);
    this._notificaciones = this._notificaciones.map((notificacion) =>
      notificacion.idNotificacion === idNotificacion ? actualizada : notificacion,
    );
    this._notificar();
    return actualizada;
  }

  listar() {
    return [...this._notificaciones];
  }

  contarNoLeidas() {
    return this._notificaciones.filter((notificacion) => !notificacion.leido).length;
  }

  suscribir(callback) {
    this._listeners.add(callback);
    return () => this._listeners.delete(callback);
  }

  iniciarPolling(intervaloMs = 30000) {
    this.detenerPolling();
    this._intervaloId = setInterval(() => this.cargar(), intervaloMs);
  }

  detenerPolling() {
    if (this._intervaloId !== null) {
      clearInterval(this._intervaloId);
      this._intervaloId = null;
    }
  }

  _notificar() {
    for (const callback of this._listeners) {
      callback(this._notificaciones);
    }
  }
}
