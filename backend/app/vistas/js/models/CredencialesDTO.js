import { ApiException } from "../utils/ApiException.js";
import { Validators } from "../utils/Validators.js";

export class CredencialesDTO {
  constructor(email, password) {
    if (!Validators.esEmailValido(email)) {
      throw new ApiException("VALIDACION", "El email no tiene un formato valido");
    }
    if (!Validators.esNoVacio(password)) {
      throw new ApiException("VALIDACION", "La contrasena no puede estar vacia");
    }
    this.email = email.trim().toLowerCase();
    this.password = password;
  }

  toJSON() {
    return { email: this.email, password: this.password };
  }
}
