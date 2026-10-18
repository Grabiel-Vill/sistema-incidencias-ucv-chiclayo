import { ApiException } from "../utils/ApiException.js";
import { Validators } from "../utils/Validators.js";

export class LaboratorioDTO {
  constructor(nombre, pabellon, piso, estadoOperativo = true, idLaboratorio = null) {
    if (!Validators.esNoVacio(nombre)) {
      throw new ApiException("VALIDACION", "El nombre del laboratorio no puede estar vacio");
    }
    if (!Validators.esNoVacio(pabellon)) {
      throw new ApiException("VALIDACION", "El pabellon no puede estar vacio");
    }
    if (!Number.isInteger(piso) || piso < 0) {
      throw new ApiException("VALIDACION", "El piso no puede ser negativo");
    }
    this.idLaboratorio = idLaboratorio;
    this.nombre = nombre.trim();
    this.pabellon = pabellon.trim();
    this.piso = piso;
    this.estadoOperativo = estadoOperativo;
  }

  toJSON() {
    return { nombre: this.nombre, pabellon: this.pabellon, piso: this.piso, estado_operativo: this.estadoOperativo };
  }

  static fromJSON(json) {
    return new LaboratorioDTO(json.nombre, json.pabellon, json.piso, json.estado_operativo, json.id_laboratorio);
  }
}
