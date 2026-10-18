import { ApiException } from "../utils/ApiException.js";
import { Validators } from "../utils/Validators.js";

export class EquipoDTO {
  constructor(codigoPatrimonial, tipoEquipo, estado = "OPERATIVO", idEquipo = null) {
    if (!Validators.esNoVacio(codigoPatrimonial)) {
      throw new ApiException("VALIDACION", "El codigo patrimonial no puede estar vacio");
    }
    if (!Validators.esNoVacio(tipoEquipo)) {
      throw new ApiException("VALIDACION", "El tipo de equipo no puede estar vacio");
    }
    this.idEquipo = idEquipo;
    this.codigoPatrimonial = codigoPatrimonial.trim();
    this.tipoEquipo = tipoEquipo.trim();
    this.estado = estado;
  }

  toJSON() {
    return { codigo_patrimonial: this.codigoPatrimonial, tipo_equipo: this.tipoEquipo, estado: this.estado };
  }

  static fromJSON(json) {
    return new EquipoDTO(json.codigo_patrimonial, json.tipo_equipo, json.estado, json.id_equipo);
  }
}
