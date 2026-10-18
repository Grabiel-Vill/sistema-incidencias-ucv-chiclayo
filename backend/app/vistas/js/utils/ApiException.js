export class ApiException extends Error {
  constructor(codigo, mensaje, statusHttp) {
    super(mensaje || "Error de comunicacion con el servidor");
    this.name = "ApiException";
    this.codigo = codigo || "ERROR_DESCONOCIDO";
    this.statusHttp = statusHttp;
  }
}
