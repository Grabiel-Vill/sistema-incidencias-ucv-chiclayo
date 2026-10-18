import { ApiException } from "../utils/ApiException.js";
import { Validators } from "../utils/Validators.js";

export class NotaTecnicaDTO {
  constructor(contenido, esPrivado = true, idNota = null) {
    if (!Validators.esNoVacio(contenido)) {
      throw new ApiException("VALIDACION", "El contenido de la nota no puede estar vacio");
    }
    this.idNota = idNota;
    this.contenido = contenido.trim();
    this.esPrivado = esPrivado;
  }

  toJSON() {
    return { contenido: this.contenido, es_privado: this.esPrivado };
  }

  static fromJSON(json) {
    return new NotaTecnicaDTO(json.contenido, json.es_privado, json.id_nota);
  }
}
