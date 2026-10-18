export class TokenDTO {
  constructor(accessToken, rol, expiracion, tipo = "Bearer") {
    this.accessToken = accessToken;
    this.rol = rol;
    this.expiracion = expiracion;
    this.tipo = tipo;
  }

  static fromJSON(json) {
    return new TokenDTO(json.access_token, json.rol, json.expiracion, json.tipo);
  }
}
