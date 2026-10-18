export class UsuarioDTO {
  constructor(idUsuario, codigoUcv, nombre, apellido, email, rol, estado, especialidad = null) {
    this.idUsuario = idUsuario;
    this.codigoUcv = codigoUcv;
    this.nombre = nombre;
    this.apellido = apellido;
    this.email = email;
    this.rol = rol;
    this.estado = estado;
    this.especialidad = especialidad;
  }

  get nombreCompleto() {
    return `${this.nombre} ${this.apellido}`;
  }

  static fromJSON(json) {
    return new UsuarioDTO(
      json.id_usuario,
      json.codigo_ucv,
      json.nombre,
      json.apellido,
      json.email,
      json.rol,
      json.estado,
      json.especialidad || null,
    );
  }
}
